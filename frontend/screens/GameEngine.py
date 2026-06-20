# ─── game_engine.py ───────────────────────────────────────────────────────────
import time
import pygame

from config import *
from models import ParticipantData
from eeg_interface import EEGInterface
from input_manager import InputManager
from game_logic import PlayerController, ObstacleManager, CollisionSystem
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_car, draw_obstacle, draw_road
from screens import ResultsScreen

class GameEngine:
    """Runs one session. Returns True if the user requests a restart."""

    def __init__(self, screen: pygame.Surface, participant: ParticipantData, eeg: EEGInterface = None):
        self._screen      = screen
        self._participant = participant
        self._eeg         = eeg or EEGInterface()
        self._fonts       = make_fonts()

    def run(self) -> bool:
        input_mgr  = InputManager(self._eeg)
        player     = PlayerController()
        obstacles  = ObstacleManager()
        collisions = CollisionSystem()
        metrics    = MetricsLogger()

        clock         = pygame.time.Clock()
        session_start = time.time()
        dash_offset   = 0.0
        obs_speed     = (OBSTACLE_HIT_Y - OBSTACLE_SPAWN_Y) / OBSTACLE_TRAVEL_TIME


        while True:
            dt        = clock.tick(FPS) / 1000.0
            game_time = time.time() - session_start
            remaining = max(0.0, MATCH_DURATION - game_time)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return False

            input_mgr.poll(pygame.event.get())
            cmd = input_mgr.get_player_command()
            if cmd and player.apply_command(cmd):
                metrics.log_lane_change(game_time, player.lane)

            if remaining > 0:
                obstacles.update(game_time, dt)

            for obs in collisions.check(player, obstacles.obstacles, game_time):
                metrics.log_collision(game_time, player.lane, obs)

            for obs in obstacles.remove_passed():
                if obs.lane != player.lane:
                    metrics.log_avoidance(game_time, player.lane, obs)
                elif not obs.hit:
                    metrics.log_collision(game_time, player.lane, obs)

            dash_offset += obs_speed * dt
            self._screen.fill(C_BG)
            draw_road(self._screen, dash_offset)

            # ─── 1. DETERMINAZIONE DEL CUE VISIVO (FRECCIA) ───
            cue_direction = None
            if remaining > 0 and obstacles.obstacles:
                # Filtra gli ostacoli non ancora superati e prendi il più vicino (y maggiore)
                valid_obstacles = [o for o in obstacles.obstacles if o.y - OBS_H/2 < PLAYER_Y + CAR_H/2]
                if valid_obstacles:
                    next_obstacle = max(valid_obstacles, key=lambda o: o.y)
                    
                    # Se l'ostacolo è a sinistra (0), la freccia deve indicare destra (1) e viceversa
                    if next_obstacle.lane == 0:
                        cue_direction = "RIGHT"
                    else:
                        cue_direction = "LEFT"

            # Render degli ostacoli e dell'auto
            for obs in obstacles.obstacles:
                draw_obstacle(self._screen, LANE_CENTERS[obs.lane], obs.y,
                              C_OBSTACLE_HIT if obs.hit else C_OBSTACLE)
            draw_car(self._screen, LANE_CENTERS[player.lane], PLAYER_Y, C_PLAYER)
            
            # ─── 2. RENDERING DELLA FRECCIA DI CUE ───
            if cue_direction:
                self.draw_cue_arrow(cue_direction)

            # draw_hud(self._screen, self._fonts, remaining,
            #          player.lane, metrics.collisions, metrics.avoidances)

            pygame.display.flip()

            if remaining <= 0:
                # Nome file fisso per raccogliere tutti i dati del software
                csv_path = metrics.export_csv(
                    self._participant,
                    "all_participants_data.csv", 
                )
                metrics.print_report()
                return ResultsScreen(self._screen, metrics, self._participant, csv_path).run()
    # ─── 3. FUNZIONE DI DISEGNO DELLA FRECCIA ───
    def draw_cue_arrow(self, direction: str) -> None:
        """Disegna una freccia geometrica o testuale al centro dello schermo."""
        center_x = ROAD_X + ROAD_W // 2
        center_y = WINDOW_H // 4 # Posizionata leggermente sopra il centro geometrico
        
        # Colore vibrante per attirare l'attenzione del soggetto (es. il tuo C_ACCENT o Verde)
        arrow_color = C_CUE 
        
        if direction == "LEFT":
            # Disegno di una freccia verso sinistra usando i poligoni di Pygame
            points = [
                (center_x + 30, center_y - 15), # Coda superiore
                (center_x - 10, center_y - 15), # Inizio punta sup
                (center_x - 10, center_y - 30), # Punta esterna sup
                (center_x - 40, center_y),      # Estremo punta
                (center_x - 10, center_y + 30), # Punta esterna inf
                (center_x - 10, center_y + 15), # Inizio punta inf
                (center_x + 30, center_y + 15), # Coda inferiore
            ]
        else: # RIGHT
            # Disegno di una freccia verso destra
            points = [
                (center_x - 30, center_y - 15),
                (center_x + 10, center_y - 15),
                (center_x + 10, center_y - 30),
                (center_x + 40, center_y),
                (center_x + 10, center_y + 30),
                (center_x + 10, center_y + 15),
                (center_x - 30, center_y + 15),
            ]
            
        pygame.draw.polygon(self._screen, arrow_color, points)
        # Un piccolo bordo scuro opzionale per staccare dallo sfondo
        pygame.draw.polygon(self._screen, C_BG, points, 2)

        