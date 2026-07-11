import pygame

from config import *
from eeg_interface import EEGInterface
from renderer import make_fonts, center_text, divider, _animate_click, draw_button, draw_step_indicator, draw_theme_toggle
from config import toggle_theme
from .utils import _handle_quit

class SignalQualityCheck:

    def __init__(self, screen: pygame.Surface, eeg: EEGInterface):
        self._screen = screen
        self._eeg = eeg
        self._fonts = make_fonts()
        self._clock = pygame.time.Clock()
        self._btn_rect = pygame.Rect(0, 0, 0, 0)
        self._animate_click = _animate_click.__get__(self)  # Bind the method to the instance
        self._clicked_btn = None
        self._theme_toggle_rect = pygame.Rect(0, 0, 0, 0)

    def run(self):
        self._eeg.connect()
        while True:
            rect_width = WINDOW_W * 0.50
            rect_left = WINDOW_W * 0.25

            rect_top = HEADER_Y + int(WINDOW_H * 0.04)

            rect_height = FOOTER_Y - rect_top - int(WINDOW_H * 0.04)

            rect = pygame.Rect(int(rect_left), int(rect_top),

                            int(rect_width), int(rect_height))

            self._draw(rect)  # Usa il metodo di disegno del quality screen
            pygame.display.flip()
            self._clock.tick(FPS)

            for ev in pygame.event.get():
                _handle_quit(ev)

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        self._animate_click("confirm")
                        return "confirm"
                    elif ev.key == pygame.K_ESCAPE:
                        self._animate_click("back")
                        return "back"

                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._theme_toggle_rect.collidepoint(ev.pos):
                        toggle_theme()
                        continue
                    if self._btn_rect.collidepoint(ev.pos):
                        self._animate_click("confirm")
                        return "confirm"
                    elif self._back_rect.collidepoint(ev.pos):
                        self._animate_click("back")
                        return "back"

    def _draw(self, rect: pygame.Rect = None):
        font_b, font, font_s = self._fonts
        s = self._screen

        # ── Sfondo principale ────────────────────────────────────────────────
        self._screen.fill(THEME["C_BG"])
        self._theme_toggle_rect = draw_theme_toggle(self._screen)

        # ── Header ───────────────────────────────────────────────────────────
        center_text(self._screen, "SIGNAL QUALITY CHECK", font_b, THEME["C_TEXT"], 40)
        draw_step_indicator(self._screen, 3, 4, font_s)
        divider(self._screen, HEADER_Y)

        if rect is not None:
            self._cached_rect = rect
        elif not hasattr(self, "_cached_rect") or self._cached_rect is None:
            # Fallback iniziale se nessuno ha mai passato un rect prima d'ora
            card_w = min(590, WINDOW_W - 40)
            card_h = FOOTER_Y - HEADER_Y - 40
            card_x = WINDOW_W // 2 - card_w // 2
            card_y = HEADER_Y + 10
            self._cached_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        
        # Da qui in poi usiamo il rect garantito e non-None
        active_rect = self._cached_rect

        # ── Dati EEG ─────────────────────────────────────────────────────────
        qualities = self._eeg.get_channel_quality()
        channels = EEGInterface.CHANNELS
        avg_quality = sum(qualities) / len(qualities) if qualities else 0

        # ── Palette di stato (Colori Flat Moderni) ───────────────────────────
        def status_color(q):
            if q >= 80:
                return (94, 211, 153)    # verde
            elif q >= 50:
                return (235, 186, 99)    # giallo
            else:
                return (227, 122, 122)   # rosso

        # ── Calcolo Altezza Dinamica della Card ────────
        base_h = active_rect.height

        padding_top = int(base_h * 0.06)
        padding_bottom = int(base_h * 0.06)
        gap_between_sections = int(base_h * 0.04)
        row_h = int(base_h * 0.08)
        avg_box_h = int(base_h * 0.18)

        channels_total_h = len(channels) * row_h

        dynamic_card_h = (
            padding_top +
            channels_total_h +
            gap_between_sections +
            avg_box_h +
            padding_bottom
        )

        panel = pygame.Rect(active_rect.x, active_rect.y + 10, active_rect.width, dynamic_card_h)
        start_y = panel.y + padding_top

        # Disegno Card Principale (Flat)
        pygame.draw.rect(self._screen, THEME["C_INPUT_BG"], panel, border_radius=14)
        pygame.draw.rect(self._screen, THEME["C_INPUT_BORDER"], panel, width=1, border_radius=14)

        panel_w = panel.width - 60
        panel_x = panel.x + 30

        # ── Ciclo Canali EEG ─────────────────────────────────────────────────
        for i, (channel, quality) in enumerate(zip(channels, qualities)):
            y = start_y + i * row_h
            color = status_color(quality)

            # Badge canale (Flat)
            badge_rect = pygame.Rect(panel_x, y, 56, 24)
            pygame.draw.rect(self._screen, (32, 35, 44), badge_rect, border_radius=6)
            pygame.draw.rect(self._screen, (52, 56, 68), badge_rect, width=1, border_radius=6)

            txt = font_s.render(channel, True, NIGHT_THEME["C_TEXT"])
            txt_x = badge_rect.x + (badge_rect.width - txt.get_width()) // 2
            txt_y = badge_rect.y + (badge_rect.height - txt.get_height()) // 2
            self._screen.blit(txt, (txt_x, txt_y))

            # Piccolo indicatore di stato a cerchio
            dot_x = badge_rect.right + 12
            dot_y = badge_rect.centery
            pygame.draw.circle(self._screen, color, (dot_x, dot_y), 4)

            # Progress bar
            bar_x = dot_x + 14
            percent_w = 56
            bar_h = 10
            bar_w = panel_w - (bar_x - panel_x) - percent_w
            bar_y = y + (badge_rect.height - bar_h) // 2

            bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
            pygame.draw.rect(self._screen, (35, 38, 47), bg_rect, border_radius=5)

            if quality > 0:
                fill_w = max(bar_h, int(bar_w * (quality / 100)))
                fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
                pygame.draw.rect(self._screen, color, fill_rect, border_radius=5)

            # Percentuale numerica
            perc = font.render(f"{quality}%", True, color)
            perc_y = y + (badge_rect.height - perc.get_height()) // 2
            self._screen.blit(perc, (bar_x + bar_w + 14, perc_y))

        # ── Sotto-card AVG (Flat) ────────────────────────────────────────────
        avg_y = start_y + channels_total_h + 22
        avg_panel = pygame.Rect(panel_x, avg_y, panel_w, 68)
        avg_color = status_color(avg_quality)

        pygame.draw.rect(self._screen, THEME["C_INPUT_ACTIVE"], avg_panel, border_radius=10)
        pygame.draw.rect(self._screen, avg_color, avg_panel, width=1, border_radius=10)

        # Testi AVG
        avg_txt = font.render("TOTAL", True, THEME["C_TEXT"])
        label_x = avg_panel.x + 34
        label_y = avg_y + 24
        self._screen.blit(avg_txt, (label_x, label_y))

        # Barra della media totale (Flat)
        avg_bar_x = label_x + 90
        avg_percent_w = 78
        avg_bar_w = avg_panel.width - (avg_bar_x - avg_panel.x) - avg_percent_w - 18
        avg_bar_h = 16
        avg_bar_y = avg_panel.y + (avg_panel.height - avg_bar_h) // 2

        pygame.draw.rect(self._screen, (40, 43, 53), (avg_bar_x, avg_bar_y, avg_bar_w, avg_bar_h), border_radius=6)
        if avg_quality > 0:
            avg_fill_w = max(avg_bar_h, int(avg_bar_w * (avg_quality / 100)))
            pygame.draw.rect(self._screen, avg_color, (avg_bar_x, avg_bar_y, avg_fill_w, avg_bar_h), border_radius=6)

        # Testo percentuale totale
        avg_perc = font_b.render(f"{avg_quality:.0f}%", True, avg_color)
        avg_perc_y = avg_panel.y + (avg_panel.height - avg_perc.get_height()) // 2
        self._screen.blit(avg_perc, (avg_bar_x + avg_bar_w + 16, avg_perc_y))

        # ── Divider Footer ───────────────────────────────────────────────────
        divider(self._screen, FOOTER_Y)

        # ── Pulsanti di navigazione ──────────────────────────────────────────
        self._back_rect = draw_button(
            s,
            "BACK",
            font_b,
            (WINDOW_W // 2 - 130, FOOTER_Y + 75),
            secondary=True,
            pressed=(self._clicked_btn == "back")
        )

        self._btn_rect = draw_button(
            s,
            "CONFIRM",
            font_b,
            (WINDOW_W // 2 + 130, FOOTER_Y + 75),
            pressed=(self._clicked_btn == "confirm")
        )