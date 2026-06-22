# ─── input_manager.py ─────────────────────────────────────────────────────────
# Bridges control sources (EEG OSC) to player commands.
# EEG predictions take priority; keyboard fallback can be added here.

from typing import Optional
from eeg_interface import EEGInterface
import pygame

class InputManager:

    def __init__(self, eeg: EEGInterface, use_keyboard: bool = False):
        self._eeg     = eeg
        self._pending: Optional[str] = None
        self._use_keyboard = use_keyboard

    def poll(self, events: list) -> None:
        if self._use_keyboard:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        self._pending = "LEFT"
                    elif e.key == pygame.K_RIGHT:
                        self._pending = "RIGHT"
            return

        pred = self._eeg.get_prediction()
        if pred in ("LEFT", "RIGHT"):
            self._pending = pred

    def get_player_command(self) -> Optional[str]:
        cmd, self._pending = self._pending, None
        return cmd