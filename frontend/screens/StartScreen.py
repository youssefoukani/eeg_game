import pygame

from config import *
from models import ParticipantData

from renderer import make_fonts, center_text, divider
from .utils import _handle_quit

class StartScreen:
    """Shows participant summary and game rules. ENTER or click to begin."""

    def __init__(self, screen: pygame.Surface, participant: ParticipantData):
        self._screen      = screen
        self._participant = participant
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()
        self._btn_rect    = pygame.Rect(0, 0, 0, 0)

    def run(self) -> None:
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            for ev in pygame.event.get():
                _handle_quit(ev)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    return
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._btn_rect.collidepoint(ev.pos):
                        return

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s, p = self._screen, self._participant
        s.fill(C_BG)

        y = 40
        center_text(s, "EEG BCI RUNNER",         font_b, C_TEXT,  y); y += 32
        center_text(s, "Motor Imagery Prototype", font_s, C_MUTED, y); y += 36
        divider(s, y); y += 20

        for line in (
            f"Participant  : {p.user_id}",
            f"Age          : {p.age}    Sex: {p.sex}",
            f"Dominant hand: {p.dominant_hand}",
        ):
            s.blit(font_s.render(line, True, C_MUTED), (80, y)); y += 22
        y += 12; divider(s, y); y += 20

        for label, val in (
            ("Duration",      f"{MATCH_DURATION // 60} min  ({MATCH_DURATION} s)"),
            ("Lanes",         "LEFT   and   RIGHT"),
            ("Obstacle time", f"{OBSTACLE_TRAVEL_TIME:.1f} s approach window"),
            ("Collisions",    "counted — game continues"),
            ("Controls",      "← Left Arrow    → Right Arrow"),
        ):
            lbl_s = font_s.render(f"{label:<16}", True, C_MUTED)
            val_s = font.render(val, True, C_TEXT)
            s.blit(lbl_s, (80, y))
            s.blit(val_s, (80 + lbl_s.get_width(), y)); y += 28

        y += 10; divider(s, y); y += 20
        center_text(s, "Switch lanes BEFORE the obstacle reaches you.", font_s, C_MUTED, y); y += 22
        center_text(s, "No need for fast reflexes — plan ahead.",        font_s, C_MUTED, y); y += 36

        self._btn_rect = pygame.Rect(WINDOW_W // 2 - 110, y, 220, 40)
        pygame.draw.rect(s, C_ACCENT, self._btn_rect, border_radius=6)
        ts = font_b.render("ENTER  —  START", True, C_BG)
        s.blit(ts, (self._btn_rect.centerx - ts.get_width() // 2, self._btn_rect.y + 11))
