import pygame
from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_button, center_text, divider
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
        
        self._play_count = play_count          # quante partite ha già giocato
        self._can_restart = play_count < 2      # True solo se ha giocato meno di 2 volte
        

    def run(self) -> bool:
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(30)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                        return False
                    if self._can_restart and ev.key in (pygame.K_r, pygame.K_RETURN):
                        return True
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._can_restart and self._btn_restart and self._btn_restart.collidepoint(ev.pos):
                        return True
                    if self._btn_quit.collidepoint(ev.pos):
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

        rows = [
            ("Participant", self._participant.user_id, C_TEXT),
            ("Total obstacles", str(m.collisions + m.avoidances), C_TEXT),
            ("Collisions", str(m.collisions), C_WARNING),
            ("Successful avoids", str(m.avoidances), C_ACCENT),
            ("Lane changes", str(m.lane_changes), C_TEXT),
        ]

        for label, value, color in rows:
            s.blit(font_s.render(label, True, C_MUTED), (card.x + 30, y))
            value_surface = font_s.render(value, True, color)
            s.blit(value_surface, (card.right - 30 - value_surface.get_width(), y))
            y += 30

        y += 8
        pygame.draw.line(s, C_INPUT_BORDER, (card.x + 20, y), (card.right - 20, y), 1)
        y += 16

        s.blit(font_s.render("CSV", True, C_MUTED), (card.x + 30, y))
        csv_value = font_s.render(str(self._csv_path), True, C_TEXT)
        max_w = card.width - 60
        if csv_value.get_width() > max_w:
            path_str = str(self._csv_path)
            while font_s.size("…" + path_str)[0] > max_w and len(path_str) > 1:
                path_str = path_str[1:]
            csv_value = font_s.render("…" + path_str, True, C_TEXT)
        s.blit(csv_value, (card.right - 30 - csv_value.get_width(), y))

        # ==========================================================
        # FOOTER
        # ==========================================================
        divider(s, FOOTER_Y)

        from renderer import draw_button

        if self._can_restart:
            # Due bottoni affiancati: QUIT a sinistra, RESTART a destra
            self._btn_quit = draw_button(
                s, "Q — QUIT", font_b,
                (WINDOW_W // 2 - 130, FOOTER_Y + 75),
                padding=28, secondary=True,
            )
            self._btn_restart = draw_button(
                s, "RESTART", font_b,
                (WINDOW_W // 2 + 130, FOOTER_Y + 75),
                padding=28,
            )
        else:
            # Solo QUIT, centrato, nessun RESTART disponibile
            self._btn_restart = None
            self._btn_quit = draw_button(
                s, "QUIT", font_b,
                (WINDOW_W // 2, FOOTER_Y + 75),
                padding=28, secondary=True,
            )