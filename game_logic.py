# ─── game_logic.py ────────────────────────────────────────────────────────────
# Core gameplay subsystems: player movement, obstacle lifecycle, collision.

import random
from typing import Optional

from config import (
    LANE_LEFT, LANE_RIGHT, LANE_CENTERS,
    OBSTACLE_SPAWN_Y, OBSTACLE_HIT_Y, OBSTACLE_TRAVEL_TIME,
    SPAWN_MIN, SPAWN_MAX, WINDOW_H, OBS_H,
)
from models import Obstacle


class PlayerController:

    def __init__(self):
        self.lane = LANE_LEFT
        self.x    = float(LANE_CENTERS[self.lane])

    def apply_command(self, cmd: Optional[str]) -> bool:
        """Move to the requested lane. Returns True if the lane actually changed."""
        if cmd == "LEFT" and self.lane != LANE_LEFT:
            self.lane = LANE_LEFT
            self.x    = float(LANE_CENTERS[self.lane])
            return True
        if cmd == "RIGHT" and self.lane != LANE_RIGHT:
            self.lane = LANE_RIGHT
            self.x    = float(LANE_CENTERS[self.lane])
            return True
        return False


class ObstacleManager:

    def __init__(self):
        self.obstacles: list[Obstacle] = []
        self._next_spawn = 0.0
        self._speed      = (OBSTACLE_HIT_Y - OBSTACLE_SPAWN_Y) / OBSTACLE_TRAVEL_TIME

    def update(self, game_time: float, dt: float) -> None:
        """Spawn new obstacles and advance all active ones."""
        if game_time >= self._next_spawn:
            self.obstacles.append(Obstacle(
                lane=random.randint(0, 1),
                y=float(OBSTACLE_SPAWN_Y),
                speed=self._speed,
                spawned_at=game_time,
            ))
            self._next_spawn = game_time + random.uniform(SPAWN_MIN, SPAWN_MAX)

        for obs in self.obstacles:
            obs.y += obs.speed * dt

    def remove_passed(self) -> list[Obstacle]:
        """Remove and return obstacles that have scrolled off the bottom."""
        passed         = [o for o in self.obstacles if o.y > WINDOW_H + OBS_H]
        self.obstacles = [o for o in self.obstacles if o.y <= WINDOW_H + OBS_H]
        return passed


class CollisionSystem:

    def check(
        self,
        player: PlayerController,
        obstacles: list[Obstacle],
        game_time: float,
    ) -> list[Obstacle]:
        """
        Mark obstacles that crossed OBSTACLE_HIT_Y and return those
        that are in the same lane as the player (actual collisions).
        Collision does NOT stop the game.
        """
        hits = []
        for obs in obstacles:
            if obs.y >= OBSTACLE_HIT_Y and not obs.hit:
                obs.hit = True
                if obs.lane == player.lane:
                    hits.append(obs)
        return hits