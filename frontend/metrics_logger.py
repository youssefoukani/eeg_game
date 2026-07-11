# ─── metrics_logger.py ────────────────────────────────────────────────────────
import csv
from typing import Optional
import os
from models import MetricEvent, Obstacle, ParticipantData


class MetricsLogger:

    def __init__(self):
        self.events:      list[MetricEvent] = []
        self.collisions   = 0
        self.avoidances   = 0
        self.lane_changes = 0
        self._rts:        list[float] = []

        self.obstacle_results = []

    # ── logging ───────────────────────────────────────────────────────────────

    def log_lane_change(self, t: float, lane: int) -> None:
        self.lane_changes += 1
        self.events.append(MetricEvent(t, "lane_change", lane))

    def log_collision(self, t: float, lane: int, obs: Obstacle) -> None:

        self.collisions += 1

        self._log_rt(t, obs)

        self.obstacle_results.append({"collision_time": round(t, 3), "avoidance_time": ""})

        self.events.append(MetricEvent(t, "collision", lane, obs.lane, t - obs.spawned_at))

    def log_avoidance(self, t: float, lane: int, obs: Obstacle) -> None:

        self.avoidances += 1

        self._log_rt(t, obs)

        self.obstacle_results.append({"collision_time": "", "avoidance_time": round(t, 3)})

        self.events.append(MetricEvent(t, "avoidance", lane, obs.lane, t - obs.spawned_at))

    def _log_rt(self, t: float, obs: Obstacle) -> None:
        self._rts.append(t - obs.spawned_at)

    
    # ── output ────────────────────────────────────────────────────────────────

    def export_csv(self, participant: ParticipantData, path: str) -> str:
        # Controlla se il file esiste già e non è vuoto
        file_exists = os.path.exists(path) and os.path.getsize(path) > 0

        header = [
            "user_id",
            "age",
            "sex",
            "dominant_hand",
            "educational_level",
            "collisions",
            "avoidances",
            "lane_changes",
        ]
        for i in range(1, 10):
            header.extend([
                f"obs{i}_collision_time",
                f"obs{i}_avoidance_time"
            ])
        
        # Apre il file in modalità "append" ('a') per non sovrascrivere
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            
            # Scrivi l'intestazione SOLO se il file è nuovo o vuoto
            if not file_exists:
                w.writerow(header)
                
            # Scrive un'unica riga con le metriche globali del partecipante

            row = [
                participant.user_id,
                participant.age,
                participant.sex,
                participant.dominant_hand,
                participant.educational_level,
                self.collisions,
                self.avoidances,
                self.lane_changes,
            ]

            for result in self.obstacle_results:
                row.extend([
                    result["collision_time"],
                    result["avoidance_time"]
                ])
            while len(self.obstacle_results) < 10:

                row.extend(["", ""])

                self.obstacle_results.append({})

            w.writerow(row)
                
        return path
    def print_report(self) -> None:
        print("\n" + "═" * 50)
        print(f"  Total obstacles   : {self.collisions + self.avoidances}")
        print(f"  Collisions        : {self.collisions}")
        print(f"  Successful avoids : {self.avoidances}")
        
        print(f"  Lane changes      : {self.lane_changes}")
        print("═" * 50)