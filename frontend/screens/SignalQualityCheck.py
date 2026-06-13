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

    def _draw_quality_card(self, rect: pygame.Rect):
        pygame.draw.rect(
            self._screen,
            (28, 30, 38),
            rect,
            border_radius=18,
        )

        pygame.draw.rect(
            self._screen,
            (55, 58, 70),
            rect,
            width=2,
            border_radius=18,
        )

    def _draw_channel_quality(
        self,
        x: int,
        y: int,
        width: int,
        channel: str,
        quality: int,
        font,
        font_small,
    ):

        BAR_H = 18
        LABEL_W = 60
        PERCENT_W = 60

        if quality >= 80:
            color = (46, 204, 113)
        elif quality >= 50:
            color = (241, 196, 15)
        else:
            color = (231, 76, 60)

        txt = font.render(channel, True, C_TEXT)
        self._screen.blit(txt, (x, y - 2))

        bar_x = x + LABEL_W
        bar_w = width - LABEL_W - PERCENT_W

        bg_rect = pygame.Rect(bar_x, y, bar_w, BAR_H)

        pygame.draw.rect(
            self._screen,
            (45, 45, 55),
            bg_rect,
            border_radius=BAR_H // 2,
        )

        fill_w = int(bar_w * quality / 100)

        fill_rect = pygame.Rect(
            bar_x,
            y,
            fill_w,
            BAR_H,
        )

        pygame.draw.rect(
            self._screen,
            color,
            fill_rect,
            border_radius=BAR_H // 2,
        )

        perc = font_small.render(f"{quality}%", True, C_TEXT)
        self._screen.blit(perc, (bar_x + bar_w + 10, y - 2))

    def _draw(self, rect: pygame.Rect = None, show_button: bool = True):

        font_b, font, font_s = self._fonts
        if show_button:
            self._screen.fill(C_BG)  # standalone: pulisce tutto
        else:
            pygame.draw.rect(self._screen, C_BG, rect)  # embedded: pulisce solo il suo rect

        pygame.draw.rect(self._screen, C_BG, rect)

        qualities = self._eeg.get_channel_quality()
        channels = EEGInterface.CHANNELS

        panel = pygame.Rect(
            rect.x,       # ← usa la X del rect passato
            rect.y + 10,
            rect.width,   # ← usa la larghezza del rect passato
            rect.height,  # ← usa l'altezza del rect passato
        )

        self._draw_quality_card(panel)

        panel_w = panel.width - 60
        panel_x = panel.x + 30

        start_y = panel.y + 25
        row_h = 28

        for i, (channel, quality) in enumerate(zip(channels, qualities)):
            self._draw_channel_quality(
                panel_x,
                start_y + i * row_h,
                panel_w,
                channel,
                quality,
                font,
                font_s,
            )

        
        if show_button:
            # Titolo della pagina
            center_text(
                self._screen,
                "SIGNAL QUALITY CHECK",
                font_b,
                C_TEXT,
                40
            )

            # ── Pulsante Adattivo ─────────────────────────────────────────────
            from renderer import draw_button
            
            # Disegna il bottone centrato (posizione y=500 per dargli spazio sotto la griglia)
            self._btn_rect = draw_button(
                self._screen, 
                "CONTINUE", 
                font_b, 
                (WINDOW_W // 2, WINDOW_H*2//3), 
                padding=30
            )
        else:
            self._btn_rect = pygame.Rect(0, 0, 0, 0)