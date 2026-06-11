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
            rect=pygame.Rect(0, 150, WINDOW_W, WINDOW_H)

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

        pygame.draw.rect(self._screen, C_BG, rect)

        
        qualities = self._eeg.get_channel_quality()

        channels = EEGInterface.CHANNELS

        
        start_y = 120

        box_w = 80
        box_h = 60
        gap = 30

        grid_total_w = (4 * box_w) + (3 * gap)

        start_x = rect.x + (rect.width - grid_total_w) // 2
        start_y = rect.y + 20

        for i, (name, quality) in enumerate(zip(channels, qualities)):

            row = i // 4
            col = i % 4

            x = start_x + col * (box_w + gap)
            y = start_y + row * (box_h + 40)

            if quality >= 80:
                color = (0, 180, 0)

            elif quality >= 50:
                color = (220, 180, 0)

            else:
                color = (200, 40, 40)

            pygame.draw.rect(
                self._screen,
                color,
                (x, y, box_w, box_h),
                border_radius=8
            )

            label = font.render(name, True, C_TEXT)
            self._screen.blit(
                label,
                (
                    x + box_w // 2 - label.get_width() // 2,
                    y + 10
                )
            )

            value = font_s.render(
                f"{quality}%",
                True,
                C_TEXT
            )

            self._screen.blit(
                value,
                (
                    x + box_w // 2 - value.get_width() // 2,
                    y + 45
                )
            )

        
        if show_button:

            center_text(
                self._screen,
                "SIGNAL QUALITY CHECK",
                font_b,
                C_TEXT,
                40
            )

            self._btn_rect = pygame.Rect(
                WINDOW_W // 2 - 110,
                400,
                220,
                40
            )

            pygame.draw.rect(
                self._screen,
                C_ACCENT,
                self._btn_rect,
                border_radius=6
            )

            txt = font_b.render(
                "CONTINUE",
                True,
                C_BG
            )

            self._screen.blit(
                txt,
                (
                    self._btn_rect.centerx - txt.get_width() // 2,
                    self._btn_rect.centery - txt.get_height() // 2
                )
            )
        else:
            self._btn_rect = pygame.Rect(0, 0, 0, 0)
