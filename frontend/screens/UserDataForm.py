import time
import pygame
import sys

from config import *
from models import ParticipantData
from .utils import _handle_quit
from renderer import make_fonts, center_text, divider, draw_button


class UserDataForm:
    """
    Collects participant metadata.

    Keyboard:
      ↑ / ↓ or TAB / SHIFT-TAB  – move between fields
      ← / →                      – cycle selector options
      BACKSPACE                  – delete last character
      ENTER                      – confirm and advance
      ESC                        – ask to quit (with confirmation)

    Mouse:
      Click on any text-box / selector button to focus / select it.
    """

    _FIELDS = ["user_id", "age"]
    _SEX    = ["M", "F", "Other"]
    _HAND   = ["Right", "Left"]
    _EDU    = ["Middle School", "High School Diploma", "Degree"]

    # Field index constants for clarity
    _F_UID, _F_AGE, _F_SEX, _F_HAND, _F_EDU = 0, 1, 2, 3, 4

    def __init__(self, screen: pygame.Surface):
        self._screen  = screen
        self._fonts   = make_fonts()
        self._clock   = pygame.time.Clock()
        self._texts   = {"user_id": "", "age": ""}
        self._sex_idx = 0
        self._hand_idx= 0
        self._edu_idx = 0
        self._focus   = 0
        self._error   = ""

        self._confirm_quit = False
        self._confirm_idx  = 1   # 0 = "Yes, Quit", 1 = "Cancel" (default sicuro)

        self._rects: dict = {}   # key → pygame.Rect

    # ── input ──────────────────────────────────────────────────────────────────

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
                    if done == "QUIT_FORM":
                        return None  # Uscita pulita dal form
                    elif done:
                        return done
                        
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    done = self._handle_click(ev.pos)
                    if done == "QUIT_FORM":
                        return None  # Uscita pulita dal form
                    elif done:
                        return done

    # ── input ──────────────────────────────────────────────────────────────────

    def _handle_key(self, ev: pygame.event.Event):
        k = ev.key

        if self._confirm_quit:
            if k == pygame.K_ESCAPE:
                self._cancel_quit()
            elif k in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                self._confirm_idx = 1 - self._confirm_idx
            elif k == pygame.K_RETURN:
                if self._confirm_idx == 0:
                    return self._do_quit()  # Ora restituisce il comando
                else:
                    self._cancel_quit()
            return None

        # Esc = Annulla/Esci
        if k == pygame.K_ESCAPE:
            self._handle_back_or_exit()
            return None

        # Navigation
        if k in (pygame.K_DOWN, pygame.K_TAB) and not (k == pygame.K_TAB and (pygame.key.get_mods() & pygame.KMOD_SHIFT)):
            self._focus = (self._focus + 1) % 5
        elif k == pygame.K_UP or (k == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT):
            self._focus = (self._focus - 1) % 5

        # Confirm
        elif k == pygame.K_RETURN:
            return self._validate()

        # Selector cycling
        elif k == pygame.K_LEFT:
            if self._focus == self._F_SEX:
                self._sex_idx  = (self._sex_idx  - 1) % len(self._SEX)
            elif self._focus == self._F_HAND:
                self._hand_idx = (self._hand_idx - 1) % len(self._HAND)
            elif self._focus == self._F_EDU:
                self._edu_idx = (self._edu_idx - 1) % len(self._EDU)
        elif k == pygame.K_RIGHT:
            if self._focus == self._F_SEX:
                self._sex_idx  = (self._sex_idx  + 1) % len(self._SEX)
            elif self._focus == self._F_HAND:
                self._hand_idx = (self._hand_idx + 1) % len(self._HAND)
            elif self._focus == self._F_EDU:
                self._edu_idx = (self._edu_idx + 1) % len(self._EDU)

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

    def _handle_click(self, pos: tuple):
        """Focus a field or toggle a selector option on mouse click."""

        # 1. SE IL POPUP E' APERTO
        # Ignoriamo del tutto il dizionario completo per evitare 
        # che elementi nascosti "rubino" il click. Controlliamo 
        # SOLO le coordinate esatte dei due bottoni del popup.
        if self._confirm_quit:
            if "confirm_quit_yes" in self._rects and self._rects["confirm_quit_yes"].collidepoint(pos):
                return self._do_quit()
            
            if "confirm_quit_no" in self._rects and self._rects["confirm_quit_no"].collidepoint(pos):
                self._cancel_quit()
                
            return None # Blocca qualsiasi altro click se il popup è aperto

        # 2. SE IL POPUP E' CHIUSO (comportamento normale)
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
                elif key.startswith("edu_"):
                    self._focus   = self._F_EDU
                    self._edu_idx = int(key.split("_")[1])
                elif key == "submit":
                    return self._validate()
                elif key == "back_exit":
                    self._handle_back_or_exit()
                break
        return None

    # ── back / exit ──────────────────────────────────────────────────────────────

    def _handle_back_or_exit(self) -> None:
        is_first_screen = getattr(self, "_is_first_screen", True)

        if is_first_screen:
            self._confirm_quit = True
            self._confirm_idx  = 1
        else:
            self._go_back()

    def _do_quit(self):
        # Inserisce un evento QUIT (lo stesso che si genera cliccando la X della finestra)
        # nella coda di Pygame. La tua funzione _handle_quit lo intercetterà all'istante.
        chiusura_evento = pygame.event.Event(pygame.QUIT)
        pygame.event.post(chiusura_evento)

    def _cancel_quit(self) -> None:
        self._confirm_quit = False

    # ── validation ─────────────────────────────────────────────────────────────

    def _validate(self):
        uid = self._texts["user_id"].strip()
        age = self._texts["age"].strip()
        if not uid:
            self._error = "User ID cannot be empty."; return None
        if not age.isdigit() or not (1 <= int(age) <= 120):
            self._error = "Age must be a number between 1 and 120."; return None
        return ParticipantData(
            user_id=uid,
            age=age,
            sex=self._SEX[self._sex_idx],
            dominant_hand=self._HAND[self._hand_idx],
            educational_level=self._EDU[self._edu_idx],
        )

    # ── drawing ────────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        font_b, font, font_s = self._fonts
        s = self._screen

        s.fill(C_BG)

        # HEADER
        center_text(s, "PARTICIPANT REGISTRATION", font_b, C_TEXT, 38)
        divider(s, HEADER_Y)

        # LAYOUT CONSTANTS
        TOP_PAD = 35
        BOTTOM_PAD = 35
        LABEL_H = 24
        BOX_H = 44
        FIELD_GAP = 28
        SEL_LABEL_GAP = 22
        SEL_H = 44
        SEL_GAP = 30

        n_fields = len(self._FIELDS)

        natural_h = (
            TOP_PAD
            + n_fields * (LABEL_H + BOX_H + FIELD_GAP)
            + 3 * (SEL_LABEL_GAP + SEL_H + SEL_GAP)
            + BOTTOM_PAD
        )

        # CARD CENTRALE
        card_w = min(590, WINDOW_W - 40)
        card_x = WINDOW_W // 2 - card_w // 2

        available_h = FOOTER_Y - HEADER_Y - 20

        scale = min(1.0, available_h / natural_h) if natural_h > 0 else 1.0
        scale = max(scale, 0.55)

        card_h = min(int(natural_h * scale) + 20, available_h)
        card_y = HEADER_Y + (FOOTER_Y - HEADER_Y - card_h) // 2

        card = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(s, C_INPUT_BG, card, border_radius=10)
        pygame.draw.rect(s, C_INPUT_BORDER, card, 1, border_radius=10)

        field_w = card_w - 60
        field_x = card_x + 30
        y = card_y + int(TOP_PAD * scale)

        labels = {
            "user_id": "User ID",
            "age": "Age",
            "educational level": "Educational Level"
        }

        # TEXT FIELDS
        for i, key in enumerate(self._FIELDS):

            active = self._focus == i

            lbl = font_s.render(
                labels[key],
                True,
                C_ACCENT if active else C_TEXT
            )

            s.blit(lbl, (field_x, y))
            y += int(LABEL_H * scale)

            box_h = max(int(BOX_H * scale), 40)
            box = pygame.Rect(field_x, y, field_w, box_h)

            pygame.draw.rect(
                s,
                C_INPUT_ACTIVE if active else C_INPUT_BG,
                box,
                border_radius=6
            )

            pygame.draw.rect(
                s,
                C_ACCENT if active else C_INPUT_BORDER,
                box,
                3 if active else 1,
                border_radius=6
            )

            cursor = "|" if active and int(time.time() * 2) % 2 == 0 else ""

            txt = font.render(
                self._texts[key] + cursor,
                True,
                C_TEXT
            )

            s.blit(txt, (box.x + 12, box.y + max(box_h - txt.get_height(), 0) // 2))

            self._rects[key] = box

            y += box_h + int(FIELD_GAP * scale)

        # SELECTOR
        def draw_selector(options, sel_idx, focus_idx, prefix, y_pos, height):

            active = self._focus == focus_idx

            spacing = 8
            btn_w = (field_w - spacing * (len(options) - 1)) // len(options)

            for i, opt in enumerate(options):

                bx = field_x + i * (btn_w + spacing)
                rect = pygame.Rect(bx, y_pos, btn_w, height)
                selected = i == sel_idx

                bg = (
                    C_INPUT_SEL
                    if selected
                    else (C_INPUT_ACTIVE if active else C_INPUT_BG)
                )

                pygame.draw.rect(s, bg, rect, border_radius=6)

                pygame.draw.rect(
                    s,
                    C_ACCENT if active else C_INPUT_BORDER,
                    rect,
                    3 if selected else 1,
                    border_radius=6
                )

                # CORREZIONE: Rimossa l'icona Unicode non compatibile e sostituita con ">"
                label_text = opt

                ts = font_s.render(
                    label_text,
                    True,
                    C_TEXT if selected else C_MUTED
                )

                s.blit(
                    ts,
                    (
                        rect.centerx - ts.get_width() // 2,
                        rect.centery - ts.get_height() // 2,
                    ),
                )

                self._rects[f"{prefix}_{i}"] = rect

        sel_h = max(int(SEL_H * scale), 38)

        # SEX
        active = self._focus == self._F_SEX
        s.blit(
            font_s.render("Sex", True, C_ACCENT if active else C_TEXT),
            (field_x, y)
        )
        y += int(SEL_LABEL_GAP * scale)
        draw_selector(self._SEX, self._sex_idx, self._F_SEX, "sex", y, sel_h)
        y += sel_h + int(SEL_GAP * scale)

        # HAND
        active = self._focus == self._F_HAND
        s.blit(
            font_s.render("Dominant Hand", True, C_ACCENT if active else C_TEXT),
            (field_x, y)
        )
        y += int((SEL_LABEL_GAP - 2) * scale)
        draw_selector(self._HAND, self._hand_idx, self._F_HAND, "hand", y, sel_h)
        y += sel_h + int(SEL_GAP * scale)

        # EDUCATION
        active = self._focus == self._F_EDU
        s.blit(
            font_s.render("Educational Level", True, C_ACCENT if active else C_TEXT),
            (field_x, y)
        )
        y += int((SEL_LABEL_GAP - 2) * scale)
        draw_selector(self._EDU, self._edu_idx, self._F_EDU, "edu", y, sel_h)

        # FOOTER
        divider(s, FOOTER_Y)

        if self._error:
            # CORREZIONE: Sostituito \u26A0 con !
            center_text(s, f"! {self._error}", font_s, C_WARNING, FOOTER_Y + 15)

        # CORREZIONE: Sostituito \u26A0 con !
        back_exit_btn_rect = draw_button(
            s, "QUIT", font_b,
            (WINDOW_W // 2 - 130, FOOTER_Y + 75),
            secondary=True,
        )
        self._rects["back_exit"] = back_exit_btn_rect

        confirm_btn_rect = draw_button(
            s, "CONFIRM", font_b,
            (WINDOW_W // 2 + 130, FOOTER_Y + 75),
        )
        self._rects["submit"] = confirm_btn_rect

        if self._confirm_quit:
            self._draw_confirm_quit_popup(font_b, font, font_s)

    def _draw_confirm_quit_popup(self, font_b, font, font_s) -> None:
        s = self._screen

        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        s.blit(overlay, (0, 0))

        dlg_w, dlg_h = 460, 190
        dlg_x = WINDOW_W // 2 - dlg_w // 2
        dlg_y = WINDOW_H // 2 - dlg_h // 2
        dlg = pygame.Rect(dlg_x, dlg_y, dlg_w, dlg_h)

        pygame.draw.rect(s, C_INPUT_BG, dlg, border_radius=12)
        pygame.draw.rect(s, C_INPUT_BORDER, dlg, 1, border_radius=12)

        title = font.render("Are you sure you want to quit?", True, C_TEXT)
        s.blit(title, (dlg.centerx - title.get_width() // 2, dlg_y + 28))

        subtitle = font_s.render(
            "Unsaved data will be lost.", True, C_MUTED
        )
        s.blit(subtitle, (dlg.centerx - subtitle.get_width() // 2, dlg_y + 62))

        btn_y = dlg_y + dlg_h - 60

        # CORREZIONE: Sostituito \u26A0 con ! per evitare crash nei calcoli di larghezza del font
        yes_rect = draw_button(
            s, "YES, QUIT", font_b,
            (dlg.centerx - 100, btn_y),
            secondary=True,
        )
        self._rects["confirm_quit_yes"] = yes_rect

        cancel_rect = draw_button(
            s, "CANCEL", font_b,
            (dlg.centerx + 100, btn_y),
        )
        self._rects["confirm_quit_no"] = cancel_rect

        highlight_rect = yes_rect if self._confirm_idx == 0 else cancel_rect
        pygame.draw.rect(s, C_ACCENT, highlight_rect, 2, border_radius=8)