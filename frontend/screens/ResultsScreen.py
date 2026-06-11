import pygame

from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from renderer import make_fonts

from .utils import _handle_quit

class ResultsScreen:
    """Post-session summary. ENTER / R = restart, Q / ESC = quit. Buttons also clickable."""

    _BTN_W, _BTN_H = 180, 40

    def __init__(self, screen: pygame.Surface, metrics: MetricsLogger,
                 participant: ParticipantData, csv_path: str):
        self._screen      = screen
        self._metrics     = metrics
        self._participant = participant
        self._csv_path    = csv_path
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()
        self._btn_restart = pygame.Rect(0, 0, 0, 0)
        self._btn_quit    = pygame.Rect(0, 0, 0, 0)

    def run(self) -> bool:
        lines = self._build_lines()
        while True:
            font_b, font, _ = self._fonts
            self._screen.fill(C_BG)
            y = 60
            for text, fnt, col in lines:
                if text:
                    ts = fnt.render(text, True, col)
                    self._screen.blit(ts, (WINDOW_W // 2 - ts.get_width() // 2, y))
                y += 36 if fnt is font_b else 30

            # Draw clickable buttons
            gap = 20
            total_w = self._BTN_W * 2 + gap
            bx = WINDOW_W // 2 - total_w // 2
            self._btn_restart = pygame.Rect(bx,                    y, self._BTN_W, self._BTN_H)
            self._btn_quit    = pygame.Rect(bx + self._BTN_W + gap, y, self._BTN_W, self._BTN_H)

            pygame.draw.rect(self._screen, C_ACCENT,  self._btn_restart, border_radius=6)
            pygame.draw.rect(self._screen, C_WARNING, self._btn_quit,    border_radius=6)

            for btn, label in ((self._btn_restart, "ENTER — RESTART"),
                               (self._btn_quit,    "Q  —  QUIT")):
                ts = font_b.render(label, True, C_BG)
                self._screen.blit(ts, (btn.centerx - ts.get_width() // 2, btn.y + 11))

            pygame.display.flip()
            self._clock.tick(30)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_q, pygame.K_ESCAPE):  return False
                    if ev.key in (pygame.K_r, pygame.K_RETURN):  return True
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._btn_restart.collidepoint(ev.pos):   return True
                    if self._btn_quit.collidepoint(ev.pos):       return False

    def _build_lines(self) -> list:
        font_b, font, _ = self._fonts
        m   = self._metrics
        
        return [
            ("SESSION COMPLETE",                                  font_b, C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"Participant        {self._participant.user_id}",   font,   C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"Total obstacles    {m.collisions + m.avoidances}", font,   C_TEXT),
            (f"Collisions         {m.collisions}",                font,   C_WARNING if m.collisions else C_TEXT),
            (f"Successful avoids  {m.avoidances}",                font,   C_ACCENT),
            (f"Accuracy           {m.accuracy:.1f}%",             font_b, C_ACCENT if m.accuracy >= 70 else C_WARNING),
            ("",                                                  font,   C_MUTED),
            
            (f"Lane changes       {m.lane_changes}",              font,   C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"CSV → {self._csv_path}",                           font,   C_MUTED),
            ("",                                                  font,   C_MUTED),
        ]