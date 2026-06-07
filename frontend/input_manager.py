# ─── input_manager.py ─────────────────────────────────────────────────────────
# Bridges control sources (EEG OSC) to player commands.
# EEG predictions take priority; keyboard fallback can be added here.

from typing import Optional
from eeg_interface import EEGInterface


class InputManager:

    def __init__(self, eeg: EEGInterface):
        self._eeg     = eeg
        self._pending: Optional[str] = None

    def poll(self, events: list) -> None:
        pred = self._eeg.get_prediction()
        if pred in ("LEFT", "RIGHT"):
            self._pending = pred

    def get_player_command(self) -> Optional[str]:
        cmd, self._pending = self._pending, None
        return cmd