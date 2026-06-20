import pygame
from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_button
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

            gap = 60 
            y_pos = y + 25
            
            # 1. Pulsante RESTART
            self._btn_restart = draw_button(
                self._screen, "ENTER — RESTART", font_b, 
                (WINDOW_W // 2 - (self._BTN_W // 2) - (gap // 2), y_pos), 
                padding=20
            )
            
            # 2. Pulsante QUIT
            self._btn_quit = draw_button(
                self._screen, "Q  —  QUIT", font_b, 
                (WINDOW_W // 2 + (self._BTN_W // 2) + (gap // 2), y_pos), 
                padding=20
            )
            pygame.draw.rect(self._screen, C_WARNING, self._btn_quit, border_radius=8)
            
            ts_quit = font_b.render("Q  —  QUIT", True, C_BG)
            self._screen.blit(ts_quit, (self._btn_quit.centerx - ts_quit.get_width() // 2, 
                                        self._btn_quit.centery - ts_quit.get_height() // 2))
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
            (f"Collisions         {m.collisions}",                font,   C_WARNING),
            (f"Successful avoids  {m.avoidances}",                font,   C_ACCENT),
            
            (f"Lane changes       {m.lane_changes}",              font,   C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"CSV → {self._csv_path}",                           font,   C_MUTED),
            ("",                                                  font,   C_MUTED),
        ]