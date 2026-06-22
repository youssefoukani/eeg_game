# ─── game_logic.py ────────────────────────────────────────────────────────────
import random
from typing import Optional

from config import *
from models import Obstacle


class PlayerController:
    def __init__(self):
        self.lane = LANE_LEFT
        # La posizione attuale (quella che disegni)
        self.x = float(LANE_CENTERS[LANE_LEFT])
        # La posizione di destinazione
        self.target_x = float(LANE_CENTERS[LANE_LEFT])
        # Velocità di spostamento (regola questo valore per la fluidità)
        self.smoothness = 0.2 

    @property
    def is_moving(self):
        # Restituisce True se la differenza è significativa
        return abs(self.x - self.target_x) > 2.0
        
    def apply_command(self, cmd: Optional[str]) -> bool:
        """Imposta solo la destinazione, non la posizione immediata."""
        target_lane = {"LEFT": LANE_LEFT, "RIGHT": LANE_RIGHT}.get(cmd)
        
        if target_lane is not None and target_lane != self.lane:
            self.lane = target_lane
            self.target_x = float(LANE_CENTERS[target_lane])
            return True
        return False

    def update(self):
        """Da chiamare in ogni frame del gioco."""
        # Se siamo lontani dal target, ci avviciniamo gradualmente
        if abs(self.x - self.target_x) > 0.1:
            # Interpolazione lineare: ci spostiamo di una percentuale della distanza
            self.x += (self.target_x - self.x) * self.smoothness
        else:
            self.x = self.target_x


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
        
        passed = []

        for o in self.obstacles:

            if (not o.passed and o.y - OBS_H / 2 > PLAYER_Y + CAR_H / 2):
                o.passed = True
                passed.append(o)

        self.obstacles = [o for o in self.obstacles if o.y <= WINDOW_H + OBS_H]

        return passed


class CollisionSystem:

    def check(self, player: PlayerController, obstacles: list[Obstacle], _: float) -> list[Obstacle]:
        # Definiamo i confini dell'auto in base alla sua posizione fluida x
        p_left   = player.x - CAR_W // 2
        p_right  = player.x + CAR_W // 2
        p_top    = PLAYER_Y - CAR_H // 2
        p_bottom = PLAYER_Y + CAR_H // 2
        
        hits = []
        for obs in obstacles:
            if obs.hit:
                continue
                
            # Definiamo i confini dell'ostacolo (fissi nella sua corsia)
            obs_cx = float(LANE_CENTERS[obs.lane])
            o_left   = obs_cx - OBS_W // 2
            o_right  = obs_cx + OBS_W // 2
            o_top    = obs.y - OBS_H // 2
            o_bottom = obs.y + OBS_H // 2
            
            # Controllo collisione rettangolare (AABB collision)
            if (p_left < o_right and p_right > o_left and
                p_top < o_bottom and p_bottom > o_top):
                
                obs.hit = True
                hits.append(obs)
                
        return hits