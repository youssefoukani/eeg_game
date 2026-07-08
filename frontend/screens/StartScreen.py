import pygame

import config
from config import *
from models import ParticipantData

from renderer import make_fonts, center_text, divider, _animate_click
from .utils import _handle_quit

class StartScreen:
    """Shows participant summary and game rules. ENTER or click to begin."""

    def __init__(self, screen: pygame.Surface, participant: ParticipantData):
        self._screen      = screen
        self._participant = participant
        self._fonts       = make_fonts()
        self._clock       = pygame.time.Clock()
        self._btn_rect    = pygame.Rect(0, 0, 0, 0)
        self._clicked_btn = None


        self._animate_click = _animate_click.__get__(self)  # Bind the method to the instance

    def run(self) -> None:
        self._btn_rect = pygame.Rect(0, 0, 0, 0)
        
        while True:
            self._draw()
            pygame.display.flip()
            self._clock.tick(FPS)
            
            for ev in pygame.event.get():
                _handle_quit(ev)
                
                # 1. Gestione della tastiera (Tasto INVIO)
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        self._animate_click("confirm")
                        return "confirm"
                    elif ev.key == pygame.K_ESCAPE:
                            self._animate_click("back")
                            return "back"
                    
                # 2. Gestione del mouse (Click sinistro sul pulsante)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
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

        s, p = self._screen, self._participant

        s.fill(THEME["C_BG"])

        # ==========================================================

        # HEADER

        # ==========================================================

        center_text(s, "EEG BCI RUNNER", font_b, THEME["C_TEXT"], 40)

        from renderer import draw_button

       

        divider(s, HEADER_Y)

        card_w = 560

        card_x = WINDOW_W // 2 - card_w // 2
        
        card_h = 220

        card_y = 200

        # ==========================================================

        # PARTICIPANT CARD

        # ==========================================================

        participant_card = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(

            s,

            THEME["C_INPUT_BG"],

            participant_card,

            border_radius=10

        )

        pygame.draw.rect(

            s,

            THEME["C_INPUT_BORDER"],

            participant_card,

            1,

            border_radius=10

        )

        y = participant_card.y + 18

        s.blit(

            font.render("Participant", True, THEME["C_ACCENT"]),

            (participant_card.x + 20, y)

        )

        y += 38

        infos = [

            ("User ID", p.user_id),

            ("Age", str(p.age)),

            ("Sex", p.sex),

            ("Dominant hand", p.dominant_hand),

            ("Educational level", p.educational_level),

        ]

        for label, value in infos:

            s.blit(

                font_s.render(label, True, THEME["C_MUTED"]),

                (participant_card.x + 30, y)

            )

            value_surface = font_s.render(value, True, THEME["C_TEXT"])

            s.blit(

                value_surface,

                (

                    participant_card.right - 30 - value_surface.get_width(),

                    y,

                ),

            )

            y += 30

        # ==========================================================

        # INSTRUCTIONS CARD

        # ==========================================================

        instructions_card = pygame.Rect(card_x, card_y + card_h + 20, card_w, 220)

        pygame.draw.rect(

            s,

            THEME["C_INPUT_BG"],

            instructions_card,

            border_radius=10

        )

        pygame.draw.rect(

            s,

            THEME["C_INPUT_BORDER"],

            instructions_card,

            1,

            border_radius=10

        )

        y = instructions_card.y + 18

        s.blit(

            font.render("Instructions", True, THEME["C_ACCENT"]),

            (instructions_card.x + 20, y)

        )

        y += 42

        instructions = [

            "THINK LEFT OR RIGHT TO AVOID INCOMING OBSTACLES!",

            "",

            "DURATION: 3 MINUTES",

            "",

            "STAY FOCUSED!",


            "",


        ]

        for line in instructions:

            color = THEME["C_TEXT"] if line else THEME["C_MUTED"]

            center_text(

                s,

                line,

                font_s,

                color,

                y,

            )

            y += 26

        # ==========================================================

        # START BUTTON

        # ==========================================================

        
        divider(self._screen, FOOTER_Y )
    

        theme_label = "NIGHT THEME" if config.THEME == config.NIGHT_THEME else "DAY THEME"
        self._theme_rect = draw_button(
            s,
            theme_label,
            font_s,
            (WINDOW_W - 140, HEADER_Y - 50),
            secondary=True,
        )

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
            "START",
            font_b,
            (WINDOW_W // 2 + 130, FOOTER_Y + 75),
            pressed=(self._clicked_btn == "confirm")
        )

    