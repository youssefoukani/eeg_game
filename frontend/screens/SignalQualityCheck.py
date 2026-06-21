import pygame

from config import *
from eeg_interface import EEGInterface
from renderer import make_fonts, center_text
from .utils import _handle_quit

class SignalQualityCheck:

    def __init__(self, screen: pygame.Surface, eeg: EEGInterface):
        self._screen = screen
        self._eeg = eeg
        self._fonts = make_fonts()
        self._clock = pygame.time.Clock()
        self._btn_rect = pygame.Rect(0, 0, 0, 0)

    def run(self):

        self._eeg.connect()

        while True:
            rect=pygame.Rect(WINDOW_W*1//4, 150, WINDOW_W//2, WINDOW_H//3-85)

            self._draw(rect, show_button=True)  # Usa il metodo di disegno del quality screen senza mostrare il pulsante

            pygame.display.flip()
            self._clock.tick(FPS)

            for ev in pygame.event.get():

                _handle_quit(ev)

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        return

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1 and self._btn_rect.collidepoint(ev.pos):
                        return

    def _draw(self, rect: pygame.Rect = None, show_button: bool = True):
        font_b, font, font_s = self._fonts
        if show_button:
            self._screen.fill(C_BG)
        else:
            pygame.draw.rect(self._screen, C_BG, rect)

        qualities = self._eeg.get_channel_quality()
        channels = EEGInterface.CHANNELS
        avg_quality = sum(qualities) / len(qualities) if qualities else 0

        panel = pygame.Rect(
            rect.x,
            rect.y + 10,
            rect.width,
            rect.height,
        )
        pygame.draw.rect(self._screen, (28, 30, 38), panel, border_radius=18)
        pygame.draw.rect(self._screen, (55, 58, 70), panel, width=2, border_radius=18)

        panel_w = panel.width - 60
        panel_x = panel.x + 30
        start_y = panel.y + 25
        row_h = 28

        for i, (channel, quality) in enumerate(zip(channels, qualities)):
            y = start_y + i * row_h
            if quality >= 80:
                color = (46, 204, 113)
            elif quality >= 50:
                color = (241, 196, 15)
            else:
                color = (231, 76, 60)

            txt = font.render(channel, True, C_TEXT)
            self._screen.blit(txt, (panel_x, y - 2))

            label_w = 60
            percent_w = 60
            bar_h = 18
            bar_x = panel_x + label_w
            bar_w = panel_w - label_w - percent_w

            bg_rect = pygame.Rect(bar_x, y, bar_w, bar_h)
            pygame.draw.rect(self._screen, (45, 45, 55), bg_rect, border_radius=bar_h // 2)

            fill_rect = pygame.Rect(bar_x, y, int(bar_w * quality / 100), bar_h)
            pygame.draw.rect(self._screen, color, fill_rect, border_radius=bar_h // 2)

            perc = font_s.render(f"{quality}%", True, C_TEXT)
            self._screen.blit(perc, (bar_x + bar_w + 10, y - 2))

        # ── Indicatore Media ──────────────────────────────────────────────
        avg_y = start_y + len(channels) * row_h + 60

        

        # Colore media
        if avg_quality >= 80:
            avg_color = (46, 204, 113)
        elif avg_quality >= 50:
            avg_color = (241, 196, 15)
        else:
            avg_color = (231, 76, 60)

        avg_y += 8

        self._screen.blit(font_b.render("AVG", True, avg_color), (panel_x, avg_y))

        bar_x = panel_x + 60

        bar_w = panel_w - 130

        pygame.draw.rect(self._screen, (60, 62, 75),

                        (bar_x, avg_y, bar_w, 22), border_radius=11)

        pygame.draw.rect(self._screen, avg_color,

                        (bar_x, avg_y, int(bar_w * avg_quality / 100), 22),

                        border_radius=11)

        self._screen.blit(

            font_b.render(f"{avg_quality:.0f}%", True, avg_color),

            (bar_x + bar_w + 8, avg_y)

        )
        if show_button:
            center_text(self._screen, "SIGNAL QUALITY CHECK", font_b, C_TEXT, 40)
            from renderer import draw_button
            self._btn_rect = draw_button(
                self._screen,
                "CONTINUE",
                font_b,
                (WINDOW_W // 2, WINDOW_H * 2 // 3),
                padding=30,
            )
        else:
            self._btn_rect = pygame.Rect(0, 0, 0, 0)