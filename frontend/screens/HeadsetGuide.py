import pygame

from config import *
from renderer import make_fonts, divider, center_text, round_image

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
        s = self._screen
        s.fill(C_BG)

        # ── 1. HEADER (Divider Superiore) ─────────────────────────────────────
        divider_top = 100
        divider(s, divider_top)
        center_text(s, "HEADSET FITTING GUIDE", font_b, C_TEXT, 38)

        # ── 2. FOOTER (Divider Inferiore e Bottone) ────────────────────────────
        center_pos = (WINDOW_W // 2, FOOTER_Y+75)
        divider_bottom = center_pos[1] - 70
        divider(s, FOOTER_Y)

        # Disegna il bottone e salva il rect locale
        from renderer import draw_button
        self._btn_rect = draw_button(s, "ENTER — CONTINUE", font_b, center_pos, padding=28)

        # ── 3. AREA IMMAGINI (Centrata e con angoli smussati) ──────────────────
        IMG_GAP = 16
        PAD_X   = 20
        
        space_y_top = divider_top + 10
        space_y_bottom = divider_bottom - 10
        available_h = space_y_bottom - space_y_top
        available_w = WINDOW_W - (PAD_X * 2)

        n = len(self._panels)
        panel_w = (available_w - IMG_GAP * (n - 1)) // n
        scaled_panels = []

        for surf in self._panels:
            ow, oh = surf.get_size()
            scale  = min(panel_w / ow, available_h / oh)
            nw, nh = int(ow * 0.90*scale), int(oh * 0.90*scale)
            
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
            img_y = space_y_top + (available_h - surf.get_height()) // 2
            s.blit(surf, (x, img_y))
            x += surf.get_width() + IMG_GAP