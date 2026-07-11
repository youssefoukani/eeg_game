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

    # Ciclo principale dell'applicazione
    while True:
        # Stato condiviso tra le schermate ripristinato ad ogni avvio
        state = {
            "participant": None,
        }

        step = 0
        STEPS = ["user_data", "headset_guide", "signal_quality", "start_screen", "fixation_cross"]

        # FASE 1: Schermate di setup
        while step < len(STEPS):
            current = STEPS[step]

            if current == "user_data":
                form = UserDataForm(screen)
                result = form.run()
                if result == "back":
                    pygame.quit()
                    sys.exit()
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

        # FASE 2: Partita
        while True:
            engine = GameEngine(screen, state["participant"], eeg=eeg)
            result = engine.run()

            if result is False:
                # Chiusura finestra o uscita esplicita (Q/ESC su ResultsScreen)
                pygame.quit()
                sys.exit()

            if result == "retry":
                # Prima di rigiocare, ripropone la fixation cross
                fx_result = FixationCross(screen).run()
                if fx_result == "back":
                    break
                # Rigioca lo stesso livello, stesso partecipante, dopo la fixation cross
                continue

            break

        # Il ciclo esterno riparte sempre da capo per il prossimo partecipante
        continue


if __name__ == "__main__":
    main()