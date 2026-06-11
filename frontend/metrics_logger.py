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
    def accuracy(self) -> float:
        total = self.collisions + self.avoidances
        return (self.avoidances / total * 100) if total else 100.0

    # ── output ────────────────────────────────────────────────────────────────

    def export_csv(self, participant: ParticipantData, path: str) -> str:
        # Controlla se il file esiste già e non è vuoto
        file_exists = os.path.exists(path) and os.path.getsize(path) > 0
        
        # Apri il file in modalità "append" ('a') per non sovrascrivere
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            
            # Scrivi l'intestazione SOLO se il file è nuovo o vuoto
            if not file_exists:
                w.writerow([
                    "user_id", "age", "sex", "dominant_hand", 
                    "collisions", "avoidances", "lane_changes", "accuracy"
                ])
                
            # Scrive un'unica riga con le metriche globali del partecipante
            # (Assicurati che self.collisions, self.avoidances e self.accuracy esistano dentro l'oggetto metrics)
            w.writerow([
                participant.user_id, 
                participant.age,
                participant.sex, 
                participant.dominant_hand,
                self.collisions,
                self.avoidances,
                self.lane_changes,
                f"{self.accuracy:.2f}" if isinstance(self.accuracy, float) else self.accuracy
            ])
                
        return path
    def print_report(self) -> None:
        print("\n" + "═" * 50)
        print(f"  Total obstacles   : {self.collisions + self.avoidances}")
        print(f"  Collisions        : {self.collisions}")
        print(f"  Successful avoids : {self.avoidances}")
        print(f"  Accuracy          : {self.accuracy:.1f}%")
        
        print(f"  Lane changes      : {self.lane_changes}")
        print("═" * 50)