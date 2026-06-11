import time

import pygame
from .utils import _handle_quit

from config import *


class FixationCross:
    """Black screen with '+' for CROSS_DURATION seconds (EEG baseline)."""

    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._clock  = pygame.time.Clock()
        self._big    = pygame.font.SysFont("monospace", 72, bold=True)
        self._hint   = pygame.font.SysFont("monospace", 13)

    def run(self) -> None:
        deadline = time.time() + CROSS_DURATION
        while time.time() < deadline:
            for ev in pygame.event.get():
                _handle_quit(ev)
            self._screen.fill((0, 0, 0))
            cross = self._big.render("+", True, (240, 240, 240))
            self._screen.blit(cross, (WINDOW_W // 2 - cross.get_width()  // 2,
                                      WINDOW_H // 2 - cross.get_height() // 2))
            hint = self._hint.render("fixation — relax and focus", True, (60, 60, 70))
            self._screen.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2,
                                     WINDOW_H // 2 + 60))
            pygame.display.flip()
            self._clock.tick(FPS)

