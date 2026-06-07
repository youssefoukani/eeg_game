# ─── screens.py ───────────────────────────────────────────────────────────────
import sys
import time

import pygame

from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from eeg_interface import EEGInterface
from renderer import make_fonts, center_text, divider


# ── shared helpers ─────────────────────────────────────────────────────────────

def _handle_quit(ev: pygame.event.Event) -> None:
    if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
        pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════════════════════════════
# Screen 0 – Headset Fitting Guide
# ══════════════════════════════════════════════════════════════════════════════

class HeadsetGuide:
    """
    Shows the two halves of guida_unicorn side by side.
    ENTER or click the button to continue.
    The image files are expected next to screens.py:
        guide_top.png    (upper half of the original TIFF)
        guide_bottom.png (lower half)
    """

    _IMG_FILES = ("guide_top.png", "guide_bottom.png")

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

        # ── background ─────────────────────────────────────────────────────────
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

        # ── footer button ──────────────────────────────────────────────────────
        BTN_W, BTN_H = 280, 44
        btn_y = WINDOW_H * 7/8
        self._btn_rect = pygame.Rect(WINDOW_W // 2 - BTN_W // 2, btn_y, BTN_W, BTN_H)

        # Glow effect — slightly larger rect in accent colour at low alpha
        glow = pygame.Surface((BTN_W + 12, BTN_H + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*C_ACCENT, 40), glow.get_rect(), border_radius=10)
        s.blit(glow, (self._btn_rect.x - 6, self._btn_rect.y - 6))

        pygame.draw.rect(s, C_ACCENT, self._btn_rect, border_radius=8)

        btn_font = pygame.font.SysFont("monospace", 16, bold=True)
        ts = btn_font.render("ENTER  —  CONTINUE", True, C_BG)
        s.blit(ts, (self._btn_rect.centerx - ts.get_width()  // 2,
                    self._btn_rect.centery - ts.get_height() // 2))


# ══════════════════════════════════════════════════════════════════════════════
# Screen 1 – Participant Registration Form
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# Screen 2 – Signal Quality Check (placeholder)
# ══════════════════════════════════════════════════════════════════════════════

class SignalQualityCheck:
    """Placeholder — press ENTER or click to continue."""

    def __init__(self, screen: pygame.Surface, eeg: EEGInterface):
        self._screen   = screen
        self._eeg      = eeg
        self._fonts    = make_fonts()
        self._clock    = pygame.time.Clock()
        self._btn_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def run(self) -> None:
        self._eeg.connect()
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
        center_text(s, "SIGNAL QUALITY CHECK",  font_b, C_TEXT,   WINDOW_H // 2 - 40)
        center_text(s, "[ To be implemented ]", font,   C_WARNING, WINDOW_H // 2)
        btn_y = WINDOW_H // 2 + 60
        self._btn_rect = pygame.Rect(WINDOW_W // 2 - 110, btn_y, 220, 36)
        pygame.draw.rect(s, C_ACCENT, self._btn_rect, border_radius=6)
        ts = font_b.render("ENTER  —  CONTINUE", True, C_BG)
        s.blit(ts, (self._btn_rect.centerx - ts.get_width() // 2, self._btn_rect.y + 9))


# ══════════════════════════════════════════════════════════════════════════════
# Screen 3 – Start Screen
# ══════════════════════════════════════════════════════════════════════════════

class StartScreen:
    """Shows participant summary and game rules. ENTER or click to begin."""

    def __init__(self, screen: pygame.Surface, participant: ParticipantData):
        self._screen      = screen
        self._participant = participant
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()
        self._btn_rect    = pygame.Rect(0, 0, 0, 0)

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
        s, p = self._screen, self._participant
        s.fill(C_BG)

        y = 40
        center_text(s, "EEG BCI RUNNER",         font_b, C_TEXT,  y); y += 32
        center_text(s, "Motor Imagery Prototype", font_s, C_MUTED, y); y += 36
        divider(s, y); y += 20

        for line in (
            f"Participant  : {p.user_id}",
            f"Age          : {p.age}    Sex: {p.sex}",
            f"Dominant hand: {p.dominant_hand}",
        ):
            s.blit(font_s.render(line, True, C_MUTED), (80, y)); y += 22
        y += 12; divider(s, y); y += 20

        for label, val in (
            ("Duration",      f"{MATCH_DURATION // 60} min  ({MATCH_DURATION} s)"),
            ("Lanes",         "LEFT   and   RIGHT"),
            ("Obstacle time", f"{OBSTACLE_TRAVEL_TIME:.1f} s approach window"),
            ("Collisions",    "counted — game continues"),
            ("Controls",      "← Left Arrow    → Right Arrow"),
        ):
            lbl_s = font_s.render(f"{label:<16}", True, C_MUTED)
            val_s = font.render(val, True, C_TEXT)
            s.blit(lbl_s, (80, y))
            s.blit(val_s, (80 + lbl_s.get_width(), y)); y += 28

        y += 10; divider(s, y); y += 20
        center_text(s, "Switch lanes BEFORE the obstacle reaches you.", font_s, C_MUTED, y); y += 22
        center_text(s, "No need for fast reflexes — plan ahead.",        font_s, C_MUTED, y); y += 36

        self._btn_rect = pygame.Rect(WINDOW_W // 2 - 110, y, 220, 40)
        pygame.draw.rect(s, C_ACCENT, self._btn_rect, border_radius=6)
        ts = font_b.render("ENTER  —  START", True, C_BG)
        s.blit(ts, (self._btn_rect.centerx - ts.get_width() // 2, self._btn_rect.y + 11))


# ══════════════════════════════════════════════════════════════════════════════
# Screen 4 – Fixation Cross
# ══════════════════════════════════════════════════════════════════════════════

class FixationCross:
    """Black screen with '+' for CROSS_DURATION seconds (EEG baseline)."""

    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._clock  = pygame.time.Clock()
        self._big    = pygame.font.SysFont("monospace", 72, bold=True)
        self._hint   = pygame.font.SysFont("monospace", 13)

    def run(self) -> None:
        deadline = time.time() + CROSS_DURATION
        while time.time() < deadline:
            for ev in pygame.event.get():
                _handle_quit(ev)
            self._screen.fill((0, 0, 0))
            cross = self._big.render("+", True, (240, 240, 240))
            self._screen.blit(cross, (WINDOW_W // 2 - cross.get_width()  // 2,
                                      WINDOW_H // 2 - cross.get_height() // 2))
            hint = self._hint.render("fixation — relax and focus", True, (60, 60, 70))
            self._screen.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2,
                                     WINDOW_H // 2 + 60))
            pygame.display.flip()
            self._clock.tick(FPS)


# ══════════════════════════════════════════════════════════════════════════════
# Screen 5 – Results
# ══════════════════════════════════════════════════════════════════════════════

class ResultsScreen:
    """Post-session summary. ENTER / R = restart, Q / ESC = quit. Buttons also clickable."""

    _BTN_W, _BTN_H = 180, 40

    def __init__(self, screen: pygame.Surface, metrics: MetricsLogger,
                 participant: ParticipantData, csv_path: str):
        self._screen      = screen
        self._metrics     = metrics
        self._participant = participant
        self._csv_path    = csv_path
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()
        self._btn_restart = pygame.Rect(0, 0, 0, 0)
        self._btn_quit    = pygame.Rect(0, 0, 0, 0)

    def run(self) -> bool:
        lines = self._build_lines()
        while True:
            font_b, font, _ = self._fonts
            self._screen.fill(C_BG)
            y = 60
            for text, fnt, col in lines:
                if text:
                    ts = fnt.render(text, True, col)
                    self._screen.blit(ts, (WINDOW_W // 2 - ts.get_width() // 2, y))
                y += 36 if fnt is font_b else 30

            # Draw clickable buttons
            gap = 20
            total_w = self._BTN_W * 2 + gap
            bx = WINDOW_W // 2 - total_w // 2
            self._btn_restart = pygame.Rect(bx,                    y, self._BTN_W, self._BTN_H)
            self._btn_quit    = pygame.Rect(bx + self._BTN_W + gap, y, self._BTN_W, self._BTN_H)

            pygame.draw.rect(self._screen, C_ACCENT,  self._btn_restart, border_radius=6)
            pygame.draw.rect(self._screen, C_WARNING, self._btn_quit,    border_radius=6)

            for btn, label in ((self._btn_restart, "ENTER — RESTART"),
                               (self._btn_quit,    "Q  —  QUIT")):
                ts = font_b.render(label, True, C_BG)
                self._screen.blit(ts, (btn.centerx - ts.get_width() // 2, btn.y + 11))

            pygame.display.flip()
            self._clock.tick(30)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_q, pygame.K_ESCAPE):  return False
                    if ev.key in (pygame.K_r, pygame.K_RETURN):  return True
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self._btn_restart.collidepoint(ev.pos):   return True
                    if self._btn_quit.collidepoint(ev.pos):       return False

    def _build_lines(self) -> list:
        font_b, font, _ = self._fonts
        m   = self._metrics
        art = m.avg_response_time
        return [
            ("SESSION COMPLETE",                                  font_b, C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"Participant        {self._participant.user_id}",   font,   C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"Total obstacles    {m.collisions + m.avoidances}", font,   C_TEXT),
            (f"Collisions         {m.collisions}",                font,   C_WARNING if m.collisions else C_TEXT),
            (f"Successful avoids  {m.avoidances}",                font,   C_ACCENT),
            (f"Accuracy           {m.accuracy:.1f}%",             font_b, C_ACCENT if m.accuracy >= 70 else C_WARNING),
            ("",                                                  font,   C_MUTED),
            (f"Avg response time  {art:.2f} s" if art else "Avg response time  —", font, C_TEXT),
            (f"Lane changes       {m.lane_changes}",              font,   C_TEXT),
            ("",                                                  font,   C_MUTED),
            (f"CSV → {self._csv_path}",                           font,   C_MUTED),
            ("",                                                  font,   C_MUTED),
        ]