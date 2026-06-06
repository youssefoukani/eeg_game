# ─── screens.py ───────────────────────────────────────────────────────────────
# All pre-game and post-game screens.
# Each class exposes a single run() method that blocks until the screen exits.

import sys
import time
import random

import pygame

from config import *
from models import ParticipantData
from metrics_logger import MetricsLogger
from eeg_interface import EEGInterface
from renderer import make_fonts, center_text, divider


# ─── helpers ──────────────────────────────────────────────────────────────────

def _quit_on_escape(ev: pygame.event.Event) -> None:
    if ev.type == pygame.QUIT:
        pygame.quit(); sys.exit()
    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
        pygame.quit(); sys.exit()


# ═══════════════════════════════════════════════════════════════════════════════
# Screen 1 – Participant Registration Form
# ═══════════════════════════════════════════════════════════════════════════════

class UserDataForm:
    """
    Collects participant metadata before the session.
    Navigation: TAB / SHIFT-TAB between fields, ← → to cycle options, ENTER to confirm.
    """

    _FIELDS = ["user_id", "age"]
    _SEX    = ["M", "F", "Other"]
    _HAND   = ["Right", "Left"]

    def __init__(self, screen: pygame.Surface):
        self._screen    = screen
        self._fb, self._f, self._fs = make_fonts()
        self._clock     = pygame.time.Clock()
        self._data      = ParticipantData()
        self._focus     = 0   # 0=user_id  1=age  2=sex  3=hand
        self._texts     = {"user_id": "", "age": ""}
        self._sex_idx   = 0
        self._hand_idx  = 0
        self._error     = ""

    def run(self) -> ParticipantData:
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            for ev in pygame.event.get():
                _quit_on_escape(ev)
                if ev.type == pygame.KEYDOWN:
                    self._handle_key(ev)
        # unreachable – exits via return inside _handle_key

    # ── private ───────────────────────────────────────────────────────────────

    def _handle_key(self, ev: pygame.event.Event) -> None:
        if ev.key == pygame.K_TAB:
            shift        = pygame.key.get_mods() & pygame.KMOD_SHIFT
            self._focus  = (self._focus + (-1 if shift else 1)) % 4

        elif ev.key == pygame.K_RETURN:
            if self._validate():
                # Return is caught by the caller via StopIteration trick;
                # instead we raise a sentinel that run() catches.
                raise _FormDone(self._data)

        elif ev.key == pygame.K_LEFT:
            if self._focus == 2:
                self._sex_idx  = (self._sex_idx  - 1) % len(self._SEX)
            elif self._focus == 3:
                self._hand_idx = (self._hand_idx - 1) % len(self._HAND)

        elif ev.key == pygame.K_RIGHT:
            if self._focus == 2:
                self._sex_idx  = (self._sex_idx  + 1) % len(self._SEX)
            elif self._focus == 3:
                self._hand_idx = (self._hand_idx + 1) % len(self._HAND)

        elif self._focus in (0, 1):
            key = self._FIELDS[self._focus]
            if ev.key == pygame.K_BACKSPACE:
                self._texts[key] = self._texts[key][:-1]
            else:
                ch = ev.unicode
                if key == "age" and ch.isdigit() and len(self._texts[key]) < 3:
                    self._texts[key] += ch
                elif key == "user_id" and ch.isprintable() and len(self._texts[key]) < 20:
                    self._texts[key] += ch

    def _validate(self) -> bool:
        uid = self._texts["user_id"].strip()
        age = self._texts["age"].strip()
        if not uid:
            self._error = "User ID cannot be empty."; return False
        if not age.isdigit() or not (1 <= int(age) <= 120):
            self._error = "Age must be a number (1–120)."; return False
        self._data.user_id       = uid
        self._data.age           = age
        self._data.sex           = self._SEX[self._sex_idx]
        self._data.dominant_hand = self._HAND[self._hand_idx]
        self._error = ""
        return True

    def _draw(self) -> None:
        s = self._screen
        s.fill(C_BG)
        center_text(s, "PARTICIPANT REGISTRATION", self._fb, C_TEXT, 42)
        center_text(s, "Motor Imagery BCI Protocol", self._fs, C_MUTED, 72)
        divider(s, 100)

        y       = 130
        field_w = 320
        field_x = WINDOW_W // 2 - field_w // 2

        # Text fields
        for i, key in enumerate(self._FIELDS):
            label  = {"user_id": "User ID", "age": "Age"}[key]
            active = (self._focus == i)
            s.blit(self._fs.render(label, True, C_ACCENT if active else C_TEXT),
                   (field_x, y));  y += 22
            box = pygame.Rect(field_x, y, field_w, 34)
            pygame.draw.rect(s, C_INPUT_ACTIVE if active else C_INPUT_BG, box, border_radius=4)
            pygame.draw.rect(s, C_ACCENT if active else C_INPUT_BORDER, box, 1, border_radius=4)
            cursor = "|" if active and int(time.time() * 2) % 2 == 0 else ""
            s.blit(self._f.render(self._texts[key] + cursor, True, C_TEXT),
                   (box.x + 10, box.y + 8));  y += 50

        # Selector helper
        def draw_selector(options, selected_idx, focus_idx, y_pos):
            active = (self._focus == focus_idx)
            btn_w  = field_w // len(options) - 6
            for i, opt in enumerate(options):
                bx = field_x + i * (btn_w + 9)
                sel = (i == selected_idx)
                bg  = C_INPUT_SEL if sel else (C_INPUT_ACTIVE if active else C_INPUT_BG)
                bdr = C_ACCENT    if active else C_INPUT_BORDER
                br  = pygame.Rect(bx, y_pos, btn_w, 34)
                pygame.draw.rect(s, bg, br, border_radius=4)
                pygame.draw.rect(s, bdr, br, 1, border_radius=4)
                ts  = self._fs.render(opt, True, C_TEXT if sel else C_MUTED)
                s.blit(ts, (br.centerx - ts.get_width() // 2, br.y + 9))

        # Sex
        active_sex = (self._focus == 2)
        s.blit(self._fs.render("Sex", True, C_ACCENT if active_sex else C_TEXT),
               (field_x, y));  y += 22
        draw_selector(self._SEX, self._sex_idx, 2, y);  y += 50

        # Hand
        active_hand = (self._focus == 3)
        s.blit(self._fs.render("Dominant Hand", True, C_ACCENT if active_hand else C_TEXT),
               (field_x, y));  y += 22
        draw_selector(self._HAND, self._hand_idx, 3, y);  y += 54

        # Error / hints
        divider(s, y);  y += 16
        if self._error:
            center_text(s, self._error, self._fs, C_WARNING, y);  y += 24
        center_text(s, "TAB / SHIFT-TAB  navigate fields", self._fs, C_MUTED, y);  y += 20
        center_text(s, "← →  cycle options   ENTER  confirm", self._fs, C_MUTED, y)

        # Confirm button
        btn = pygame.Rect(WINDOW_W // 2 - 80, WINDOW_H - 70, 160, 36)
        pygame.draw.rect(s, C_ACCENT, btn, border_radius=5)
        ts = self._fb.render("CONFIRM", True, C_BG)
        s.blit(ts, (btn.centerx - ts.get_width() // 2, btn.y + 9))


class _FormDone(Exception):
    def __init__(self, data: ParticipantData):
        self.data = data


# Patch run() to catch the sentinel
_original_run = UserDataForm.run
def _patched_run(self) -> ParticipantData:
    try:
        _original_run(self)
    except _FormDone as done:
        return done.data
UserDataForm.run = _patched_run


# ═══════════════════════════════════════════════════════════════════════════════
# Screen 2 – Signal Quality Check
# ═══════════════════════════════════════════════════════════════════════════════

class SignalQualityCheck:
    """
    Placeholder temporaneo per la schermata di controllo qualità del segnale EEG.
    Premere SPAZIO per continuare e avviare la sessione.
    """

    def __init__(self, screen: pygame.Surface, eeg: EEGInterface):
        self._screen = screen
        self._eeg    = eeg
        # Inizializzazione font (usa le tue funzioni di helper, es. make_fonts o _fonts)
        self._fb, self._f, self._fs = make_fonts() 
        self._clock  = pygame.time.Clock()

    def run(self) -> None:
        # Avvia la connessione in background se l'interfaccia lo richiede
        self._eeg.connect()
        
        while True:
            self._draw()
            pygame.display.flip()
            
            self._clock.tick(FPS) 
            
            for ev in pygame.event.get():
                # Mantiene la funzione di chiusura globale con ESC
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # Premendo SPAZIO si supera il placeholder e si va alla croce di fissazione
                    elif ev.key == pygame.K_SPACE: 
                        return

    def _draw(self) -> None:
        s = self._screen
        
        s.fill(C_BG) 
        
        center_text(s, "SCHERMATA QUALITY CHECK", self._fb, C_TEXT, WINDOW_H // 2 - 40)
        center_text(s, "[ Da implementare ]", self._f, C_WARNING, WINDOW_H // 2)
        
        center_text(s, "L'interfaccia OSC è attiva in background.", self._fs, C_MUTED, WINDOW_H // 2 + 60)
        center_text(s, "Premere [ SPAZIO ] per continuare", self._fs, C_ACCENT, WINDOW_H // 2 + 120)

# ═══════════════════════════════════════════════════════════════════════════════
# Screen 3 – Fixation Cross
# ═══════════════════════════════════════════════════════════════════════════════

class FixationCross:
    """
    Black screen with a white '+' for a  [CROSS_DURATION] s interval.
    Establishes a resting-state EEG baseline before task onset.
    Duration is jittered to reduce temporal expectation.
    """

    def __init__(self, screen: pygame.Surface):
        self._screen     = screen
        self._clock      = pygame.time.Clock()
        self._font_cross = pygame.font.SysFont("monospace", 72, bold=True)
        self._font_hint  = pygame.font.SysFont("monospace", 13)

    def run(self) -> None:
        deadline = time.time() + CROSS_DURATION

        while time.time() < deadline:
            for ev in pygame.event.get():
                _quit_on_escape(ev)

            self._screen.fill((0, 0, 0))

            cross = self._font_cross.render("+", True, (240, 240, 240))
            self._screen.blit(cross, (
                WINDOW_W // 2 - cross.get_width()  // 2,
                WINDOW_H // 2 - cross.get_height() // 2,
            ))
            hint = self._font_hint.render("fixation — relax and focus", True, (60, 60, 70))
            self._screen.blit(hint, (
                WINDOW_W // 2 - hint.get_width() // 2,
                WINDOW_H // 2 + 60,
            ))

            pygame.display.flip()
            self._clock.tick(FPS)


# ═══════════════════════════════════════════════════════════════════════════════
# Screen 4 – Start Screen
# ═══════════════════════════════════════════════════════════════════════════════

class StartScreen:
    """
    Shows participant summary, game rules, and waits for SPACE to begin.
    """

    def __init__(self, screen: pygame.Surface, participant: ParticipantData):
        self._screen      = screen
        self._participant = participant
        self._fb, self._f, self._fs = make_fonts()
        self._clock       = pygame.time.Clock()

    def run(self) -> None:
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            for ev in pygame.event.get():
                _quit_on_escape(ev)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    return

    def _draw(self) -> None:
        s, p = self._screen, self._participant
        s.fill(C_BG)

        y = 40
        center_text(s, "EEG BCI RUNNER",          self._fb, C_TEXT,  y); y += 32
        center_text(s, "Motor Imagery Prototype",  self._fs, C_MUTED, y); y += 36
        divider(s, y); y += 20

        for line in [
            f"Participant  : {p.user_id}",
            f"Age          : {p.age}    Sex: {p.sex}",
            f"Dominant hand: {p.dominant_hand}",
        ]:
            s.blit(self._fs.render(line, True, C_MUTED), (80, y)); y += 22
        y += 12
        divider(s, y); y += 20

        for label, val in [
            ("Duration",      f"{MATCH_DURATION // 60} min  ({MATCH_DURATION} s)"),
            ("Lanes",         "LEFT   and   RIGHT"),
            ("Obstacle time", f"{OBSTACLE_TRAVEL_TIME:.1f} s approach window"),
            ("Collisions",    "counted — game continues"),
            ("Controls",      "← Left Arrow    → Right Arrow"),
        ]:
            lbl_s = self._fs.render(f"{label:<16}", True, C_MUTED)
            val_s = self._f.render(val, True, C_TEXT)
            s.blit(lbl_s, (80, y))
            s.blit(val_s, (80 + lbl_s.get_width(), y)); y += 28

        y += 10
        divider(s, y); y += 20
        center_text(s, "Switch lanes BEFORE the obstacle reaches you.", self._fs, C_MUTED, y); y += 22
        center_text(s, "No need for fast reflexes — plan ahead.",        self._fs, C_MUTED, y); y += 36

        btn = pygame.Rect(WINDOW_W // 2 - 90, y, 180, 40)
        pygame.draw.rect(s, C_ACCENT, btn, border_radius=6)
        ts = self._fb.render("SPACE  —  START", True, C_BG)
        s.blit(ts, (btn.centerx - ts.get_width() // 2, btn.y + 11))


# ═══════════════════════════════════════════════════════════════════════════════
# Screen 5 – Results
# ═══════════════════════════════════════════════════════════════════════════════

class ResultsScreen:
    """
    Post-session summary. Q = quit, R = restart.
    Returns True if the researcher requests a restart.
    """

    def __init__(self, screen: pygame.Surface,
                 metrics: MetricsLogger,
                 participant: ParticipantData,
                 csv_path: str):
        self._screen      = screen
        self._metrics     = metrics
        self._participant = participant
        self._csv_path    = csv_path
        self._fb, self._f, _ = make_fonts()
        self._clock       = pygame.time.Clock()

    def run(self) -> bool:
        lines = self._build_lines()
        while True:
            self._screen.fill(C_BG)
            y = 60
            for text, fnt, col in lines:
                if text:
                    ts = fnt.render(text, True, col)
                    self._screen.blit(ts, (WINDOW_W // 2 - ts.get_width() // 2, y))
                y += 36 if fnt is self._fb else 30
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:      return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_q:    return False
                    if ev.key == pygame.K_r:    return True
            self._clock.tick(30)

    def _build_lines(self) -> list:
        m   = self._metrics
        art = m.avg_response_time
        return [
            ("SESSION COMPLETE",                                    self._fb, C_TEXT),
            ("",                                                    self._f,  C_MUTED),
            (f"Participant        {self._participant.user_id}",     self._f,  C_TEXT),
            ("",                                                    self._f,  C_MUTED),
            (f"Total obstacles    {m.collisions + m.avoidances}",   self._f,  C_TEXT),
            (f"Collisions         {m.collisions}",                  self._f,
             C_WARNING if m.collisions > 0 else C_TEXT),
            (f"Successful avoids  {m.avoidances}",                  self._f,  C_ACCENT),
            (f"Accuracy           {m.accuracy:.1f}%",               self._fb,
             C_ACCENT if m.accuracy >= 70 else C_WARNING),
            ("",                                                    self._f,  C_MUTED),
            (f"Avg response time  {art:.2f} s" if art
             else "Avg response time  —",                           self._f,  C_TEXT),
            (f"Lane changes       {m.lane_changes}",                self._f,  C_TEXT),
            ("",                                                    self._f,  C_MUTED),
            (f"CSV → {self._csv_path}",                             self._f,  C_MUTED),
            ("",                                                    self._f,  C_MUTED),
            ("Q  quit     R  restart",                              self._f,  C_MUTED),
        ]