import pygame
from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_button, center_text, divider, draw_theme_toggle, _animate_click
from config import toggle_theme
from .utils import _handle_quit

class ResultsScreen:
    """Post-session summary. ENTER / R = retry stesso livello, N = new session
    (torna a UserDataForm), Q / ESC / chiusura finestra = esce dall'app. Pulsanti anche cliccabili."""


    def __init__(self, screen: pygame.Surface, metrics: MetricsLogger,
                 participant: ParticipantData, csv_path: str):
        self._screen      = screen
        self._metrics     = metrics
        self._participant = participant
        self._csv_path    = csv_path
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()

        self._animate_click = _animate_click.__get__(self)  # Bind the method to the instance

        self._clicked_btn = None
        self._btn_retry = pygame.Rect(0, 0, 0, 0)
        self._btn_new_session = pygame.Rect(0, 0, 0, 0)
        self._theme_toggle_rect = pygame.Rect(0, 0, 0, 0)

    def run(self):
        """Ritorna 'retry' (rigioca subito lo stesso livello, stesso partecipante),
        'new_session' (torna a UserDataForm per un nuovo partecipante), oppure
        False se l'utente chiude la finestra o preme Q/ESC (uscita completa)."""
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
                    if ev.key in (pygame.K_r, pygame.K_RETURN):
                        self._animate_click("retry")
                        return "retry"
                    if ev.key == pygame.K_n:
                        self._animate_click("new_session")
                        return "new_session"
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._theme_toggle_rect.collidepoint(ev.pos):
                        toggle_theme()
                        continue
                    if self._btn_retry.collidepoint(ev.pos):
                        self._animate_click("retry")
                        return "retry"
                    if self._btn_new_session.collidepoint(ev.pos):
                        self._animate_click("new_session")
                        return "new_session"

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s = self._screen
        m = self._metrics

        s.fill(THEME["C_BG"])

        self._theme_toggle_rect = draw_theme_toggle(s)

        # ==========================================================
        # HEADER
        # ==========================================================
        center_text(s, "SESSION COMPLETE", font_b, THEME["C_TEXT"], 40)
        divider(s, HEADER_Y)

        # ==========================================================
        # RESULTS CARD
        # ==========================================================
        card_w = 560
        card_x = WINDOW_W // 2 - card_w // 2
        card_y = 200
        card_h = 280

        card = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(s, THEME["C_INPUT_BG"], card, border_radius=10)
        pygame.draw.rect(s, THEME["C_INPUT_BORDER"], card, 1, border_radius=10)

        y = card.y + 18
        s.blit(font.render("Summary", True, THEME["C_ACCENT"]), (card.x + 20, y))
        y += 38

        success_rate = m.avoidances / (m.collisions + m.avoidances) if (m.collisions + m.avoidances) > 0 else 0

        rows = [
            ("Participant", self._participant.user_id, THEME["C_TEXT"]),
            ("Total obstacles", str(m.collisions + m.avoidances), THEME["C_TEXT"]),
            ("Collisions", str(m.collisions), THEME["C_WARNING"]),
            ("Successful avoids", str(m.avoidances), THEME["C_ACCENT"]),
            ("Lane changes", str(m.lane_changes), THEME["C_TEXT"]),
            ("Success Rate", f"{success_rate:.2%}", THEME["C_ACCENT"]),
        ]

        for label, value, color in rows:
            s.blit(font_s.render(label, True, THEME["C_MUTED"]), (card.x + 30, y))
            value_surface = font_s.render(value, True, color)
            s.blit(value_surface, (card.right - 30 - value_surface.get_width(), y))
            y += 30

        y += 8
        pygame.draw.line(s, THEME["C_INPUT_BORDER"], (card.x + 20, y), (card.right - 20, y), 1)
        y += 16

        
        

        # ==========================================================
        # FOOTER
        # ==========================================================
        divider(s, FOOTER_Y)

        from renderer import draw_button

        # NEW SESSION a sinistra, secondario/rosso (come BACK/QUIT: esce da
        # questo partecipante e torna all'inizio del flusso). RETRY a destra,
        # primario/blu (come CONFIRM/START: prosegue in avanti).
        self._btn_new_session = draw_button(
            s, "NEW SESSION", font_b,
            (WINDOW_W // 2 - 130, FOOTER_Y + 75),
            secondary=True,
            pressed=(self._clicked_btn == "new_session")
        )
        self._btn_retry = draw_button(
            s, "RETRY", font_b,
            (WINDOW_W // 2 + 130, FOOTER_Y + 75),
            pressed=(self._clicked_btn == "retry")
        )