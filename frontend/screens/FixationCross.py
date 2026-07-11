import math
import time

import pygame
from .utils import _handle_quit

from config import *


class FixationCross:
    """Schermata di fissazione (baseline EEG): croce centrale per CROSS_DURATION
    secondi. Il colore della croce segue il tema attivo (nera in modalità
    chiara, chiara/bianca in modalità scura), così resta sempre ben visibile
    e in contrasto con lo sfondo."""

    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._clock  = pygame.time.Clock()
        self._hint   = pygame.font.SysFont("arial", 18, bold=True)

    def run(self) -> None:
        deadline = time.time() + CROSS_DURATION
        start = time.time()

        cx, cy = WINDOW_W // 2, WINDOW_H // 2
        arm_len   = 42   # lunghezza di ogni braccio della croce
        thickness = 7    # spessore dei bracci

        while time.time() < deadline:
            for ev in pygame.event.get():
                _handle_quit(ev)

            self._screen.fill(THEME["C_BG"])

            elapsed = time.time() - start
            # Leggero "respiro": la croce pulsa dolcemente per favorire il rilassamento
            pulse = 1.0 + 0.05 * math.sin(elapsed * 1.3)
            half = int(arm_len * pulse)

            cross_color = THEME["C_TEXT"]    # nero su tema chiaro, bianco su tema scuro
            glow_color  = THEME["C_ACCENT"]

            # Alone morbido dietro la croce
            glow_radius = int(60 * pulse)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, 22), (glow_radius, glow_radius), glow_radius)
            self._screen.blit(glow_surf, (cx - glow_radius, cy - glow_radius))

            # Bracci della croce con estremità arrotondate (anti-aliased)
            pygame.draw.line(self._screen, cross_color, (cx - half, cy), (cx + half, cy), thickness)
            pygame.draw.line(self._screen, cross_color, (cx, cy - half), (cx, cy + half), thickness)
            for end in ((cx - half, cy), (cx + half, cy), (cx, cy - half), (cx, cy + half)):
                pygame.draw.circle(self._screen, cross_color, end, thickness // 2)
            pygame.draw.circle(self._screen, cross_color, (cx, cy), thickness // 2 + 1)

            # Sottile anello esterno decorativo, colore accento del tema
            pygame.draw.circle(self._screen, glow_color, (cx, cy), int(90 * pulse), width=1)

            hint = self._hint.render("FIXATION — RELAX AND FOCUS", True, THEME["C_MUTED"])
            hint_pos = (cx - hint.get_width() // 2, cy + 100)
            self._screen.blit(hint, hint_pos)

            pygame.display.flip()
            self._clock.tick(FPS)