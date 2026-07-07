import pygame
from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_button, center_text, divider, _animate_click
from .utils import _handle_quit

class ResultsScreen:
    """Post-session summary. ENTER / R = restart, Q / ESC = quit. Buttons also clickable."""


    def __init__(self, screen: pygame.Surface, metrics: MetricsLogger,
                 participant: ParticipantData, csv_path: str, play_count: int):
        self._screen      = screen
        self._metrics     = metrics
        self._participant = participant
        self._csv_path    = csv_path
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()

        self._animate_click = _animate_click.__get__(self)  # Bind the method to the instance
        
        self._play_count = play_count          # quante partite ha già giocato
        self._can_restart = play_count < 2      # True solo se ha giocato meno di 2 volte

        self._clicked_btn = None
        

    def run(self) -> bool:
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(30)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._animate_click("quit")
                    return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                        self._animate_click("quit")
                        return False
                    if self._can_restart and ev.key in (pygame.K_r, pygame.K_RETURN):
                        self._animate_click("restart")
                        return True
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._can_restart and self._btn_restart and self._btn_restart.collidepoint(ev.pos):
                        self._animate_click("restart")
                        return True
                    if self._btn_quit.collidepoint(ev.pos):
                        self._animate_click("quit")
                        return False

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s = self._screen
        m = self._metrics

        s.fill(C_BG)

        # ==========================================================
        # HEADER
        # ==========================================================
        center_text(s, "SESSION COMPLETE", font_b, C_TEXT, 40)
        divider(s, HEADER_Y)

        # ==========================================================
        # RESULTS CARD
        # ==========================================================
        card_w = 560
        card_x = WINDOW_W // 2 - card_w // 2
        card_y = 200
        card_h = 280

        card = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(s, C_INPUT_BG, card, border_radius=10)
        pygame.draw.rect(s, C_INPUT_BORDER, card, 1, border_radius=10)

        y = card.y + 18
        s.blit(font.render("Summary", True, C_ACCENT), (card.x + 20, y))
        y += 38

        success_rate = m.avoidances / (m.collisions + m.avoidances) if (m.collisions + m.avoidances) > 0 else 0

        rows = [
            ("Participant", self._participant.user_id, C_TEXT),
            ("Total obstacles", str(m.collisions + m.avoidances), C_TEXT),
            ("Collisions", str(m.collisions), C_WARNING),
            ("Successful avoids", str(m.avoidances), C_ACCENT),
            ("Lane changes", str(m.lane_changes), C_TEXT),
            ("Success Rate", f"{success_rate:.2%}", C_ACCENT),
        ]

        for label, value, color in rows:
            s.blit(font_s.render(label, True, C_MUTED), (card.x + 30, y))
            value_surface = font_s.render(value, True, color)
            s.blit(value_surface, (card.right - 30 - value_surface.get_width(), y))
            y += 30

        y += 8
        pygame.draw.line(s, C_INPUT_BORDER, (card.x + 20, y), (card.right - 20, y), 1)
        y += 16

        
        

        # ==========================================================
        # FOOTER
        # ==========================================================
        divider(s, FOOTER_Y)

        from renderer import draw_button

        if self._can_restart:
            # Due bottoni affiancati: QUIT a sinistra, RESTART a destra
            self._btn_quit = draw_button(
                s, "QUIT", font_b,
                (WINDOW_W // 2 - 130, FOOTER_Y + 75),
                secondary=True,
                pressed=(self._clicked_btn == "quit")
            )
            self._btn_restart = draw_button(
                s, "RESTART", font_b,
                (WINDOW_W // 2 + 130, FOOTER_Y + 75),
                pressed=(self._clicked_btn == "restart")
            )
        else:
            # Solo QUIT, centrato, nessun RESTART disponibile
            self._btn_restart = None
            self._btn_quit = draw_button(
                s, "QUIT", font_b,
                (WINDOW_W // 2, FOOTER_Y + 75),
                secondary=True,
                pressed=(self._clicked_btn == "quit")
            )