# ─── models.py ────────────────────────────────────────────────────────────────
# Plain data containers shared across all modules.

from dataclasses import dataclass
from typing import Optional


@dataclass
class ParticipantData:
    user_id:       str = ""
    age:           str = ""
    sex:           str = ""   # "M" | "F" | "Other"
    dominant_hand: str = ""   # "Right" | "Left"


@dataclass
class Obstacle:
    lane:       int
    y:          float
    speed:      float         # px / second
    spawned_at: float         # game-clock seconds at spawn
    hit:        bool = False  # True once the obstacle crossed OBSTACLE_HIT_Y


@dataclass
class MetricEvent:
    timestamp:     float
    event_type:    str                  # "lane_change" | "collision" | "avoidance"
    player_lane:   int
    obstacle_lane: Optional[int]   = None
    response_time: Optional[float] = None  # seconds from obstacle spawn to hit-line