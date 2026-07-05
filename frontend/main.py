# ─── main.py ──────────────────────────────────────────────────────────────────
# Entry point.
#
# Pre-game pipeline:
#   1. UserDataForm       – participant registration
#   2. SignalQualityCheck – EEG OSC connection + channel quality
#   3. StartScreen        – instructions + SPACE to begin
#   4. FixationCross      – resting-state EEG baseline
#
# Run:  python main.py
# Deps: pip install pygame python-osc

import sys
import pygame

from config import WINDOW_W, WINDOW_H
from eeg_interface import EEGInterface
from screens import HeadsetGuide, UserDataForm, SignalQualityCheck, FixationCross, StartScreen, GameEngine
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("EEG BCI Runner — Motor Imagery Prototype")
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    eeg = EEGInterface()

    # Stato condiviso tra le schermate
    state = {
        "participant": None,
    }

    step = 0
    STEPS = ["user_data", "headset_guide", "signal_quality", "start_screen", "fixation_cross"]

    while step < len(STEPS):
        current = STEPS[step]

        if current == "user_data":
            form = UserDataForm(screen)
            # 🔴 Nota: se anche UserDataForm ora restituisce "back"/dati,
            # bisogna adattare questa parte (vedi nota sotto)
            result = form.run()
            if result == "back":
                # Prima schermata: non si può tornare oltre.
                # Se vuoi che "back" qui equivalga a uscire dall'app:
                break
            state["participant"] = result
            step += 1

        elif current == "headset_guide":
            result = HeadsetGuide(screen).run()
            if result == "back":
                step -= 1
            else:
                step += 1

        elif current == "signal_quality":
            result = SignalQualityCheck(screen, eeg).run()
            if result == "back":
                step -= 1
            else:
                step += 1

        elif current == "start_screen":
            result = StartScreen(screen, state["participant"]).run()
            if result == "back":
                step -= 1
            else:
                step += 1

        elif current == "fixation_cross":
            result = FixationCross(screen).run()
            if result == "back":
                step -= 1
            else:
                step += 1

    # Fine sequenza pre-gioco: avvia il game loop
    while GameEngine(screen, state["participant"], eeg=eeg).run():
        pass

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()