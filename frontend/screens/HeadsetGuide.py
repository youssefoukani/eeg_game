import pygame

import config
from config import *
from renderer import make_fonts, divider, center_text, round_image, draw_step_indicator, _animate_click

from .utils import _handle_quit

class HeadsetGuide:
    """
    Shows the two halves of guida_unicorn side by side.
    ENTER or click the button to continue.
    The image files are expected next to screens.py:
        guide_top.png    (upper half of the original TIFF)
        guide_bottom.png (lower half)
    """

    _IMG_FILES = ("../img/guide_bottom.png", "../img/guide_top.png")

    def __init__(self, screen: pygame.Surface):
        self._screen   = screen
        self._fonts    = make_fonts()
        self._clock    = pygame.time.Clock()
        self._btn_rect = pygame.Rect(0, 0, 0, 0)
        self._panels   = self._load_panels()
        self._rects = {}

        self._animate_click = _animate_click.__get__(self)  # Bind the method to the instance
        self._clicked_btn = None
    def _load_panels(self) -> list:
        import os
        panels = []
        base = os.path.dirname(os.path.abspath(__file__))
        for fname in self._IMG_FILES:
            path = os.path.join(base, fname)
            try:
                surf = pygame.image.load(path).convert_alpha()
                panels.append(surf)
            except Exception as exc:
                print(f"[HeadsetGuide] Could not load {path}: {exc}")
        return panels
    
    
    def run(self):
        while True:
            self._draw()
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

                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._btn_rect.collidepoint(ev.pos):
                        self._animate_click("confirm")
                        return "confirm"
                    elif self._back_rect.collidepoint(ev.pos):
                        self._animate_click("back")
                        return "back"
                    if self._theme_rect.collidepoint(ev.pos):

                        config.set_theme(config.THEME == config.DAY_THEME)

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s = self._screen
        s.fill(config.THEME["C_BG"])

        # ── 1. HEADER (Divider Superiore) ─────────────────────────────────────
        center_text(s, "HEADSET FITTING GUIDE", font_b, C_TEXT, 38)
        draw_step_indicator(s, 2, 4, font)
        divider(s, HEADER_Y)

        # ── 2. FOOTER (Divider Inferiore e Bottone) ────────────────────────────
        center_pos = (WINDOW_W // 2, FOOTER_Y+75)
        divider_bottom = center_pos[1] - 70
        divider(s, FOOTER_Y)

        

        # Disegna il bottone e salva il rect locale
        from renderer import draw_button
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

        theme_label = "NIGHT THEME" if config.THEME == config.NIGHT_THEME else "DAY THEME"
        self._theme_rect = draw_button(
            s,
            theme_label,
            font_s,
            (WINDOW_W - 140, HEADER_Y - 50),
            secondary=True,
        )

        # ── 3. AREA IMMAGINI (Centrata e con angoli smussati) ──────────────────
        IMG_GAP = int(WINDOW_W * 0.02)   # distanza tra immagini
        PAD_X   = int(WINDOW_W * 0.03)   # margine laterale
        base_top = HEADER_Y

        base_bottom = divider_bottom

        available_h = base_bottom - base_top

        available_w = WINDOW_W - (PAD_X * 2)


        vertical_margin = int(available_h * 0.03)
        space_y_top = base_top + vertical_margin

        space_y_bottom = base_bottom - vertical_margin

        available_h = space_y_bottom - space_y_top


        n = len(self._panels)
        panel_w = (available_w - IMG_GAP * (n - 1)) // n
        scaled_panels = []

        for surf in self._panels:
            ow, oh = surf.get_size()
            scale  = min(panel_w / ow, available_h / oh)
            scale = min(panel_w / ow, available_h / oh)

            # piccolo padding interno uniforme (non arbitrario)

            INNER_SCALE = 0.95

            nw, nh = int(ow * scale * INNER_SCALE), int(oh * scale * INNER_SCALE)
            
            # 1. Ridimensiona l'immagine
            img_scaled = pygame.transform.smoothscale(surf, (nw, nh))
            # 2. Applica gli angoli smussati (es. raggio 12px)
            img_rounded = round_image(img_scaled, radius=12)
            
            scaled_panels.append(img_rounded)

        # Calcolo X iniziale per centrare il gruppo orizzontalmente
        total_w = sum(p.get_width() for p in scaled_panels) + IMG_GAP * (n - 1)
        x = (WINDOW_W - total_w) // 2

        # Disegno dei pannelli
        for surf in scaled_panels:
            img_area_h = space_y_bottom - space_y_top

            img_y = space_y_top + (img_area_h - surf.get_height()) // 2
            s.blit(surf, (x, img_y))
            x += surf.get_width() + IMG_GAP
    