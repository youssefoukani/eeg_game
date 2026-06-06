# ─── input_manager.py ─────────────────────────────────────────────────────────
# Single integration point between the control source and the game.
#
# To switch from keyboard to EEG:
#
# Hybrid mode (keyboard + EEG simultaneously):
#   Both sources are always polled; EEG predictions take priority when present.

import pygame
from typing import Optional
from eeg_interface import EEGInterface


class InputManager:

    def __init__(self, eeg: EEGInterface):  
        self._eeg     = eeg
        self._pending: Optional[str] = None

    def poll(self, events: list) -> None:
        
        # Legge l'ultima predizione OSC — non-blocking
        pred = self._eeg.get_prediction()
        if pred in ("LEFT", "RIGHT"):
            self._pending = pred
        

    def get_player_command(self) -> Optional[str]:
        cmd = self._pending
        self._pending = None
        return cmd