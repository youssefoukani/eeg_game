import pygame

from config import *
from renderer import make_fonts

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

        # ── header card ────────────────────────────────────────────────────────
        HEADER_H = 110
        FOOTER_H = 80
        PADDING  = 16

        # Subtle card behind the title area
        card = pygame.Rect(0, 0, WINDOW_W, HEADER_H)
        pygame.draw.rect(s, C_HUD_BG, card)
        pygame.draw.line(s, C_ACCENT, (0, HEADER_H), (WINDOW_W, HEADER_H), 2)

        # Step badge — "STEP 1 of 5" style indicator
        badge_font = pygame.font.SysFont("monospace", 11, bold=True)
        badge_surf = badge_font.render("PRE-SESSION  ·  STEP 0", True, C_ACCENT)
        s.blit(badge_surf, (PADDING + 4, 14))

        # Main title — larger and prominent
        title_font = pygame.font.SysFont("monospace", 22, bold=True)
        title_surf = title_font.render("HEADSET FITTING GUIDE", True, C_TEXT)
        s.blit(title_surf, (PADDING + 4, 34))

        # Subtitle
        sub = font_s.render(
            "Put on the Unicorn Hybrid Black before continuing.", True, C_MUTED)
        s.blit(sub, (PADDING + 4, 68))

        # Right-side hint (keyboard shortcut)
        hint = font_s.render("ENTER  or  click to continue", True, C_MUTED)
        s.blit(hint, (WINDOW_W - hint.get_width() - PADDING, 14))

        # ── image area ─────────────────────────────────────────────────────────
        IMG_GAP     = 16          # gap between panels
        IMG_PAD     = 24          # horizontal margin from window edge
        available_w = WINDOW_W - IMG_PAD * 2
        available_h = WINDOW_H - HEADER_H - FOOTER_H - 16

        if self._panels:
            n       = len(self._panels)
            panel_w = (available_w - IMG_GAP * (n - 1)) // n

            scaled = []
            for surf in self._panels:
                ow, oh = surf.get_size()
                scale  = min(panel_w / ow, available_h / oh)
                nw, nh = int(ow * scale), int(oh * scale)
                scaled.append(pygame.transform.smoothscale(surf, (nw, nh)))

            # Centre the group horizontally
            total_w = sum(p.get_width() for p in scaled) + IMG_GAP * (n - 1)
            x       = (WINDOW_W - total_w) // 2
            img_top = HEADER_H + 12

            for surf in scaled:
                # Shadow / border card behind each image
                img_y   = img_top + (available_h - surf.get_height()) // 2
                border  = pygame.Rect(x - 4, img_y - 4,
                                      surf.get_width() + 8, surf.get_height() + 8)
                pygame.draw.rect(s, C_DIVIDER, border, border_radius=6)
                s.blit(surf, (x, img_y))
                x += surf.get_width() + IMG_GAP

        else:
            # ── fallback placeholder ───────────────────────────────────────────
            box = pygame.Rect(IMG_PAD, HEADER_H + 16,
                              available_w, available_h)
            pygame.draw.rect(s, C_INPUT_BG, box, border_radius=8)
            pygame.draw.rect(s, C_INPUT_BORDER, box, 1, border_radius=8)

            # Icon-like cross
            cx, cy = box.centerx, box.centery - 30
            for dx, dy, w, h in ((-24, -4, 48, 8), (-4, -24, 8, 48)):
                pygame.draw.rect(s, C_DIVIDER,
                                 pygame.Rect(cx + dx, cy + dy, w, h),
                                 border_radius=3)

            missing = font_b.render("Images not found", True, C_MUTED)
            detail  = font_s.render(
                "Place  guide_top.png  and  guide_bottom.png  next to  screens.py",
                True, C_WARNING)
            s.blit(missing, (box.centerx - missing.get_width() // 2, cy + 30))
            s.blit(detail,  (box.centerx - detail.get_width()  // 2, cy + 58))

    # ── footer button ──────────────────────────────────────────    
        # 1. Definizione font e testo
        btn_font = pygame.font.SysFont("arial", 18, bold=True) # Usa font leggibile
        btn_text = "ENTER — CONTINUE"
        
        # 2. Chiama la funzione adattiva che abbiamo creato in renderer.py
        from renderer import draw_button 
        
        # Posizione desiderata (centro orizzontale, 7/8 dell'altezza)
        center_pos = (WINDOW_W // 2, int(WINDOW_H * 7/8))
        
        # 3. Disegna il bottone e ottieni il rettangolo di collisione
        self._btn_rect = draw_button(s, btn_text, btn_font, center_pos, padding=30)
