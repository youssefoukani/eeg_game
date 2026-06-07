# ─── metrics_logger.py ────────────────────────────────────────────────────────
import csv
from typing import Optional

from models import MetricEvent, Obstacle, ParticipantData


class MetricsLogger:

    def __init__(self):
        self.events:      list[MetricEvent] = []
        self.collisions   = 0
        self.avoidances   = 0
        self.lane_changes = 0
        self._rts:        list[float] = []

    # ── logging ───────────────────────────────────────────────────────────────

    def log_lane_change(self, t: float, lane: int) -> None:
        self.lane_changes += 1
        self.events.append(MetricEvent(t, "lane_change", lane))

    def log_collision(self, t: float, lane: int, obs: Obstacle) -> None:
        self.collisions += 1
        self._log_rt(t, obs)
        self.events.append(MetricEvent(t, "collision", lane, obs.lane, t - obs.spawned_at))

    def log_avoidance(self, t: float, lane: int, obs: Obstacle) -> None:
        self.avoidances += 1
        self._log_rt(t, obs)
        self.events.append(MetricEvent(t, "avoidance", lane, obs.lane, t - obs.spawned_at))

    def _log_rt(self, t: float, obs: Obstacle) -> None:
        self._rts.append(t - obs.spawned_at)

    # ── computed ──────────────────────────────────────────────────────────────

    @property
    def avg_response_time(self) -> Optional[float]:
        return sum(self._rts) / len(self._rts) if self._rts else None

    @property
    def accuracy(self) -> float:
        total = self.collisions + self.avoidances
        return (self.avoidances / total * 100) if total else 100.0

    # ── output ────────────────────────────────────────────────────────────────

    def export_csv(self, participant: ParticipantData, path: str) -> str:
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["user_id", "age", "sex", "dominant_hand",
                        "timestamp", "event_type", "player_lane",
                        "obstacle_lane", "response_time_s"])
            for e in self.events:
                w.writerow([
                    participant.user_id, participant.age,
                    participant.sex, participant.dominant_hand,
                    f"{e.timestamp:.3f}", e.event_type, e.player_lane,
                    e.obstacle_lane if e.obstacle_lane is not None else "",
                    f"{e.response_time:.3f}" if e.response_time is not None else "",
                ])
        return path

    def print_report(self) -> None:
        art = self.avg_response_time
        print("\n" + "═" * 50)
        print(f"  Total obstacles   : {self.collisions + self.avoidances}")
        print(f"  Collisions        : {self.collisions}")
        print(f"  Successful avoids : {self.avoidances}")
        print(f"  Accuracy          : {self.accuracy:.1f}%")
        if art is not None:
            print(f"  Avg response time : {art:.2f} s")
        print(f"  Lane changes      : {self.lane_changes}")
        print("═" * 50)