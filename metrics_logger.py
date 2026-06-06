# ─── metrics_logger.py ────────────────────────────────────────────────────────
# Records all in-session events and produces a CSV report at session end.

import csv
from typing import Optional

from models import MetricEvent, Obstacle, ParticipantData


class MetricsLogger:

    def __init__(self):
        self.events:          list[MetricEvent] = []
        self.collisions       = 0
        self.avoidances       = 0
        self.lane_changes     = 0
        self._response_times: list[float] = []

    # ── logging ───────────────────────────────────────────────────────────────

    def log_lane_change(self, t: float, lane: int) -> None:
        self.lane_changes += 1
        self.events.append(MetricEvent(t, "lane_change", lane))

    def log_collision(self, t: float, lane: int, obs: Obstacle) -> None:
        self.collisions += 1
        rt = t - obs.spawned_at
        self._response_times.append(rt)
        self.events.append(MetricEvent(t, "collision", lane, obs.lane, rt))

    def log_avoidance(self, t: float, lane: int, obs: Obstacle) -> None:
        self.avoidances += 1
        rt = t - obs.spawned_at
        self._response_times.append(rt)
        self.events.append(MetricEvent(t, "avoidance", lane, obs.lane, rt))

    # ── computed properties ───────────────────────────────────────────────────

    @property
    def avg_response_time(self) -> Optional[float]:
        return (sum(self._response_times) / len(self._response_times)
                if self._response_times else None)

    @property
    def accuracy(self) -> float:
        total = self.collisions + self.avoidances
        return (self.avoidances / total * 100) if total else 100.0

    # ── output ────────────────────────────────────────────────────────────────

    def export_csv(self, participant: ParticipantData, path: str) -> str:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "user_id", "age", "sex", "dominant_hand",
                "timestamp", "event_type", "player_lane",
                "obstacle_lane", "response_time_s",
            ])
            for e in self.events:
                writer.writerow([
                    participant.user_id, participant.age,
                    participant.sex,     participant.dominant_hand,
                    f"{e.timestamp:.3f}",
                    e.event_type,
                    e.player_lane,
                    e.obstacle_lane if e.obstacle_lane is not None else "",
                    f"{e.response_time:.3f}" if e.response_time is not None else "",
                ])
        return path

    def print_report(self) -> None:
        art = self.avg_response_time
        print("\n" + "═" * 50)
        print("  SESSION REPORT")
        print("═" * 50)
        print(f"  Total obstacles   : {self.collisions + self.avoidances}")
        print(f"  Collisions        : {self.collisions}")
        print(f"  Successful avoids : {self.avoidances}")
        print(f"  Accuracy          : {self.accuracy:.1f}%")
        if art is not None:
            print(f"  Avg response time : {art:.2f} s")
        print(f"  Lane changes      : {self.lane_changes}")
        print("═" * 50)