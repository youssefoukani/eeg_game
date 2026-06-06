# ─── input_manager.py ─────────────────────────────────────────────────────────
# Single integration point between the control source and the game.
#
# To switch from keyboard to EEG:
#   Pass use_eeg=True.  No other file needs to change.
#
# Hybrid mode (keyboard + EEG simultaneously):
#   Both sources are always polled; EEG predictions take priority when present.

import pygame
from typing import Optional
from eeg_interface import EEGInterface


class InputManager:

    def __init__(self, eeg: EEGInterface, use_eeg: bool = False):
        self._eeg      = eeg
        self._use_eeg  = use_eeg
        self._pending: Optional[str] = None

    def poll(self, events: list) -> None:
        """Call once per frame with the current pygame event list."""
        # Keyboard fallback – always available for debugging
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    self._pending = "LEFT"
                elif ev.key == pygame.K_RIGHT:
                    self._pending = "RIGHT"

        # EEG prediction overwrites keyboard when enabled
        if self._use_eeg:
            pred = self._eeg.get_prediction()
            if pred in ("LEFT", "RIGHT"):
                self._pending = pred

    def get_player_command(self) -> Optional[str]:
        """Consume and return the latest command, or None if none pending."""
        cmd = self._pending
        self._pending = None
        return cmd