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
        self._btn_rect = pygame.Rect(0, 0, 0, 0)
        
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            
            for ev in pygame.event.get():
                _handle_quit(ev)
                
                # 1. Gestione della tastiera (Tasto INVIO)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    return
                    
                # 2. Gestione del mouse (Click sinistro sul pulsante)
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

        # ── Partecipante ──────────────────────────────────────────
        for line in (
            f"Participant: {p.user_id} | Age: {p.age} | Sex: {p.sex}",
            f"Dominant hand: {p.dominant_hand}",
        ):
            center_text(s, line, font_s, C_MUTED, y); y += 26
        y += 12; divider(s, y); y += 20

        # ── Regole / parametri──────────────────────────────────
        rules = [
            ("Duration", f"{MATCH_DURATION // 60} min ({MATCH_DURATION} s)"),
            ("Lanes", "LEFT and RIGHT"),
            ("Obstacle time", f"{OBSTACLE_TRAVEL_TIME:.1f} s window"),
            ("Collisions", "counted — game continues"),
            ("Controls", "← Left  |  → Right"),
        ]
        
        for label, val in rules:
            text_line = f"{label}: {val}"
            center_text(s, text_line, font, C_TEXT, y); y += 30

        y += 10; divider(s, y); y += 20
        center_text(s, "Switch lanes BEFORE the obstacle reaches you.", font_s, C_MUTED, y); y += 22
        center_text(s, "No need for fast reflexes — plan ahead.",        font_s, C_MUTED, y); y += 36

        # ── Pulsante Adattivo ─────────────────────────────────────────────────
        from renderer import draw_button
        
        # Disegnamo il bottone centrato e adattato al testo
        self._btn_rect = draw_button(
            s, 
            "ENTER  —  START", 
            font_b, 
            (WINDOW_W // 2, y + 20), 
            padding=30
        )