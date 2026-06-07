# ─── game_logic.py ────────────────────────────────────────────────────────────
import random
from typing import Optional

from config import (
    LANE_LEFT, LANE_RIGHT, LANE_CENTERS,
    OBSTACLE_SPAWN_Y, OBSTACLE_HIT_Y, OBSTACLE_TRAVEL_TIME,
    SPAWN_MIN, SPAWN_MAX, WINDOW_H, OBS_H, CAR_H, PLAYER_Y,
)
from models import Obstacle


class PlayerController:

    def __init__(self):
        self.lane = LANE_LEFT
        self.x    = float(LANE_CENTERS[LANE_LEFT])

    def apply_command(self, cmd: Optional[str]) -> bool:
        """Move to the requested lane. Returns True if the lane changed."""
        target = {"LEFT": LANE_LEFT, "RIGHT": LANE_RIGHT}.get(cmd)
        if target is not None and target != self.lane:
            self.lane = target
            self.x    = float(LANE_CENTERS[target])
            return True
        return False


class ObstacleManager:

    _SPEED = (OBSTACLE_HIT_Y - OBSTACLE_SPAWN_Y) / OBSTACLE_TRAVEL_TIME

    def __init__(self, seed: int = 42):
        self.obstacles: list[Obstacle] = []
        self._rng        = random.Random(seed)
        self._next_spawn = 0.0

    def update(self, game_time: float, dt: float) -> None:
        if game_time >= self._next_spawn:
            self.obstacles.append(Obstacle(
                lane=self._rng.randint(0, 1),
                y=float(OBSTACLE_SPAWN_Y),
                speed=self._SPEED,
                spawned_at=game_time,
            ))
            self._next_spawn = game_time + self._rng.uniform(SPAWN_MIN, SPAWN_MAX)
        for obs in self.obstacles:
            obs.y += obs.speed * dt

    def remove_passed(self) -> list[Obstacle]:
        passed         = [o for o in self.obstacles if o.y > WINDOW_H + OBS_H]
        self.obstacles = [o for o in self.obstacles if o.y <= WINDOW_H + OBS_H]
        return passed


class CollisionSystem:

    def check(self, player: PlayerController, obstacles: list[Obstacle], _: float) -> list[Obstacle]:
        player_top    = PLAYER_Y - CAR_H
        player_bottom = PLAYER_Y
        hits = []
        for obs in obstacles:
            if obs.hit or obs.lane != player.lane:
                continue
            obs_top    = obs.y - OBS_H
            obs_bottom = obs.y
            if obs_bottom >= player_top and obs_top <= player_bottom:
                obs.hit = True
                hits.append(obs)
        return hits