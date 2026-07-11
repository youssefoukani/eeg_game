import time

import pygame
from .utils import _handle_quit

from config import *


class FixationCross:
    """Black screen with '+' for CROSS_DURATION seconds (EEG baseline)."""

    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._clock  = pygame.time.Clock()
        self._big    = pygame.font.SysFont("arial", 80, bold=True)
        self._hint   = pygame.font.SysFont("arial", 18, bold=True)

    def run(self) -> None:
        deadline = time.time() + CROSS_DURATION
        while time.time() < deadline:
            for ev in pygame.event.get():
                _handle_quit(ev)
            
            self._screen.fill(THEME["C_BG"])
            
            # Croce bianca
            cross = self._big.render("+", True, (255, 255, 255))
            hint = self._hint.render("FIXATION — RELAX AND FOCUS", True, (150, 150, 150))
            
            # Calcolo posizioni centrato
            cross_pos = (WINDOW_W // 2 - cross.get_width() // 2, 
                         WINDOW_H // 2 - cross.get_height() // 2)
            hint_pos = (WINDOW_W // 2 - hint.get_width() // 2, 
                        WINDOW_H // 2 + 80)
            
            self._screen.blit(cross, cross_pos)
            self._screen.blit(hint, hint_pos)
            
            pygame.display.flip()
            self._clock.tick(FPS)