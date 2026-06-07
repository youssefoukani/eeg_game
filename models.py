# ─── models.py ────────────────────────────────────────────────────────────────
from dataclasses import dataclass, field
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
    speed:      float
    spawned_at: float
    hit:        bool = False


@dataclass
class MetricEvent:
    timestamp:     float
    event_type:    str        # "lane_change" | "collision" | "avoidance"
    player_lane:   int
    obstacle_lane: Optional[int]   = None
    response_time: Optional[float] = None