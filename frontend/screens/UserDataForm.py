import time

import pygame

from config import *
from models import ParticipantData
from .utils import _handle_quit
from renderer import make_fonts, center_text, divider



class UserDataForm:
    """
    Collects participant metadata.

    Keyboard:
      ↑ / ↓ or TAB / SHIFT-TAB  – move between fields
      ← / →                      – cycle selector options
      BACKSPACE                  – delete last character
      ENTER                      – confirm and advance

    Mouse:
      Click on any text-box / selector button to focus / select it.
    """

    _FIELDS = ["user_id", "age"]
    _SEX    = ["M", "F", "Other"]
    _HAND   = ["Right", "Left"]

    # Field index constants for clarity
    _F_UID, _F_AGE, _F_SEX, _F_HAND = 0, 1, 2, 3

    def __init__(self, screen: pygame.Surface):
        self._screen  = screen
        self._fonts   = make_fonts()
        self._clock   = pygame.time.Clock()
        self._texts   = {"user_id": "", "age": ""}
        self._sex_idx = 0
        self._hand_idx= 0
        self._focus   = 0
        self._error   = ""

        self._rects: dict = {}   # key → pygame.Rect

    def run(self) -> ParticipantData:
        while True:
            self._rects = {}
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            for ev in pygame.event.get():
                _handle_quit(ev)
                if ev.type == pygame.KEYDOWN:
                    done = self._handle_key(ev)
                    if done:
                        return done
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self._handle_click(ev.pos)

    # ── input ──────────────────────────────────────────────────────────────────

    def _handle_key(self, ev: pygame.event.Event):
        k = ev.key

        # Navigation
        if k in (pygame.K_DOWN, pygame.K_TAB) and not (k == pygame.K_TAB and (pygame.key.get_mods() & pygame.KMOD_SHIFT)):
            self._focus = (self._focus + 1) % 4
        elif k == pygame.K_UP or (k == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT):
            self._focus = (self._focus - 1) % 4

        # Confirm
        elif k == pygame.K_RETURN:
            return self._validate()

        # Selector cycling
        elif k == pygame.K_LEFT:
            if self._focus == self._F_SEX:
                self._sex_idx  = (self._sex_idx  - 1) % len(self._SEX)
            elif self._focus == self._F_HAND:
                self._hand_idx = (self._hand_idx - 1) % len(self._HAND)
        elif k == pygame.K_RIGHT:
            if self._focus == self._F_SEX:
                self._sex_idx  = (self._sex_idx  + 1) % len(self._SEX)
            elif self._focus == self._F_HAND:
                self._hand_idx = (self._hand_idx + 1) % len(self._HAND)

        # Text input
        elif self._focus in (self._F_UID, self._F_AGE):
            key = self._FIELDS[self._focus]
            if k == pygame.K_BACKSPACE:
                self._texts[key] = self._texts[key][:-1]
            else:
                ch = ev.unicode
                if key == "age" and ch.isdigit() and len(self._texts[key]) < 3:
                    self._texts[key] += ch
                elif key == "user_id" and ch.isprintable() and len(self._texts[key]) < 20:
                    self._texts[key] += ch

        return None

    def _handle_click(self, pos: tuple) -> None:
        """Focus a field or toggle a selector option on mouse click."""
        for key, rect in self._rects.items():
            if rect.collidepoint(pos):
                if key == "user_id":
                    self._focus = self._F_UID
                elif key == "age":
                    self._focus = self._F_AGE
                elif key.startswith("sex_"):
                    self._focus   = self._F_SEX
                    self._sex_idx = int(key.split("_")[1])
                elif key.startswith("hand_"):
                    self._focus    = self._F_HAND
                    self._hand_idx = int(key.split("_")[1])
                break

    # ── validation ─────────────────────────────────────────────────────────────

    def _validate(self):
        uid = self._texts["user_id"].strip()
        age = self._texts["age"].strip()
        if not uid:
            self._error = "User ID cannot be empty."; return None
        if not age.isdigit() or not (1 <= int(age) <= 120):
            self._error = "Age must be a number between 1 and 120."; return None
        return ParticipantData(
            user_id=uid, age=age,
            sex=self._SEX[self._sex_idx],
            dominant_hand=self._HAND[self._hand_idx],
        )

    # ── drawing ────────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s = self._screen
        s.fill(C_BG)
        center_text(s, "PARTICIPANT REGISTRATION", font_b, C_TEXT,   42)
        center_text(s, "Motor Imagery BCI Protocol", font_s, C_MUTED, 72)
        divider(s, 100)

        field_w = WINDOW_W // 2
        field_x = WINDOW_W // 2 - field_w // 2
        y       = WINDOW_H // 3

        # ── text fields (User ID, Age) ────────────────────────────────────────
        labels = {"user_id": "User ID", "age": "Age"}
        for i, key in enumerate(self._FIELDS):
            active = (self._focus == i)
            s.blit(font_s.render(labels[key], True, C_ACCENT if active else C_TEXT),
                   (field_x, y)); y += 22

            box = pygame.Rect(field_x, y, field_w, 34)
            pygame.draw.rect(s, C_INPUT_ACTIVE if active else C_INPUT_BG, box, border_radius=4)
            pygame.draw.rect(s, C_ACCENT if active else C_INPUT_BORDER, box, 1, border_radius=4)

            cursor = "|" if active and int(time.time() * 2) % 2 == 0 else ""
            s.blit(font.render(self._texts[key] + cursor, True, C_TEXT), (box.x + 10, box.y + 8))

            self._rects[key] = box
            y += 50

        # ── selector helper ───────────────────────────────────────────────────
        def draw_selector(options, sel_idx, focus_idx, prefix, y_pos):
            active = (self._focus == focus_idx)
            btn_w  = field_w // len(options) - 6
            for i, opt in enumerate(options):
                bx  = field_x + i * (btn_w + 9)
                sel = (i == sel_idx)
                bg  = C_INPUT_SEL if sel else (C_INPUT_ACTIVE if active else C_INPUT_BG)
                bdr = C_ACCENT    if active else C_INPUT_BORDER
                br  = pygame.Rect(bx, y_pos, btn_w, 34)
                pygame.draw.rect(s, bg, br, border_radius=4)
                pygame.draw.rect(s, bdr, br, 1, border_radius=4)
                ts  = font_s.render(opt, True, C_TEXT if sel else C_MUTED)
                s.blit(ts, (br.centerx - ts.get_width() // 2, br.y + 9))
                self._rects[f"{prefix}_{i}"] = br

        # ── Sex ───────────────────────────────────────────────────────────────
        active_sex = (self._focus == self._F_SEX)
        s.blit(font_s.render("Sex", True, C_ACCENT if active_sex else C_TEXT),
               (field_x, y)); y += 22
        draw_selector(self._SEX, self._sex_idx, self._F_SEX, "sex", y); y += 50

        # ── Dominant Hand ─────────────────────────────────────────────────────
        active_hand = (self._focus == self._F_HAND)
        s.blit(font_s.render("Dominant Hand", True, C_ACCENT if active_hand else C_TEXT),
               (field_x, y)); y += 22
        draw_selector(self._HAND, self._hand_idx, self._F_HAND, "hand", y); y += 54

        # ── footer ────────────────────────────────────────────────────────────
        divider(s, y); y += 16

        if self._error:
            center_text(s, self._error, font_s, C_WARNING, y); y += 26

        # ENTER button hint
        btn = pygame.Rect(WINDOW_W // 2 - 110, y, 220, 36)
        pygame.draw.rect(s, C_ACCENT, btn, border_radius=6)
        hint = font_b.render("ENTER  —  CONFIRM", True, C_BG)
        s.blit(hint, (btn.centerx - hint.get_width() // 2, btn.y + 9))

        # Keyboard shortcut reminder (subtle)
        y += 50
        center_text(s, "↑ ↓  navigate     ← →  cycle options     click to select",
                    font_s, C_MUTED, y)

