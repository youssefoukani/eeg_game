# ─── game_engine.py ───────────────────────────────────────────────────────────
# Main game loop. Owns the frame clock and coordinates all subsystems.

import time
import pygame

from config import (
    FPS, MATCH_DURATION, WINDOW_H,
    C_BG, C_OBSTACLE, C_OBSTACLE_HIT, C_PLAYER,
    LANE_CENTERS, PLAYER_Y,
    OBSTACLE_HIT_Y, OBSTACLE_SPAWN_Y, OBSTACLE_TRAVEL_TIME,
)
from models import ParticipantData
from eeg_interface import EEGInterface
from input_manager import InputManager
from game_logic import PlayerController, ObstacleManager, CollisionSystem
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_car, draw_obstacle, draw_road, draw_hud
from screens import ResultsScreen


class GameEngine:
    """Runs one 2-minute session. Returns True if the user requests a restart."""

    def __init__(self, screen: pygame.Surface,
                 participant: ParticipantData,
                 eeg: EEGInterface | None = None,
                 use_eeg: bool = False):
        self._screen      = screen
        self._participant = participant
        self._eeg         = eeg or EEGInterface()
        self._use_eeg     = use_eeg
        self._fonts       = make_fonts()

    def run(self) -> bool:
        # Initialise subsystems
        input_mgr   = InputManager(self._eeg, use_eeg=self._use_eeg)
        player      = PlayerController()
        obstacles   = ObstacleManager()
        collisions  = CollisionSystem()
        metrics     = MetricsLogger()

        clock         = pygame.time.Clock()
        session_start = time.time()
        dash_offset   = 0.0
        obs_speed     = (OBSTACLE_HIT_Y - OBSTACLE_SPAWN_Y) / OBSTACLE_TRAVEL_TIME

        while True:
            dt        = clock.tick(FPS) / 1000.0
            game_time = time.time() - session_start
            remaining = max(0.0, MATCH_DURATION - game_time)

            # ── events ────────────────────────────────────────────────────────
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT:
                    return False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return False

            # ── input → player ────────────────────────────────────────────────
            input_mgr.poll(events)
            cmd = input_mgr.get_player_command()
            if cmd and player.apply_command(cmd):
                metrics.log_lane_change(game_time, player.lane)

            # ── obstacle lifecycle ────────────────────────────────────────────
            if remaining > 0:
                obstacles.update(game_time, dt)

            for obs in collisions.check(player, obstacles.obstacles, game_time):
                metrics.log_collision(game_time, player.lane, obs)

            for obs in obstacles.remove_passed():
                if obs.lane != player.lane:
                    metrics.log_avoidance(game_time, player.lane, obs)
                elif not obs.hit:
                    metrics.log_collision(game_time, player.lane, obs)

            # ── render ────────────────────────────────────────────────────────
            dash_offset += obs_speed * dt
            self._screen.fill(C_BG)
            draw_road(self._screen, dash_offset)

            for obs in obstacles.obstacles:
                draw_obstacle(self._screen, LANE_CENTERS[obs.lane], obs.y,
                              C_OBSTACLE_HIT if obs.hit else C_OBSTACLE)
            draw_car(self._screen, LANE_CENTERS[player.lane], PLAYER_Y, C_PLAYER)

            draw_hud(
                self._screen, self._fonts, remaining,
                player.lane, metrics.collisions, metrics.avoidances,
                metrics.events, obstacles.obstacles,
            )
            pygame.display.flip()

            # ── session end ───────────────────────────────────────────────────
            if remaining <= 0:
                csv_path = metrics.export_csv(
                    self._participant,
                    f"session_{self._participant.user_id}_{int(time.time())}.csv",
                )
                metrics.print_report()
                return ResultsScreen(
                    self._screen, metrics, self._participant, csv_path
                ).run()