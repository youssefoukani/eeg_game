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

    # Ciclo principale dell'applicazione (permette di tornare al menu)
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
                    # Se chiudi l'app nella primissima schermata, esce completamente
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

        # FASE 2: Partite
        MAX_PLAYS = 2
        play_count = 0
        quit_to_menu = False

        while play_count < MAX_PLAYS:
            if play_count == 1:
                seed = 12
            else:
                seed = 42  # seconda partita → seed fisso

            engine = GameEngine(
                screen,
                state["participant"],
                eeg=eeg,
                seed=seed,
                play_count=play_count + 1,   # 1 = prima partita, 2 = seconda
                max_plays=MAX_PLAYS,
            )

            result = engine.run()

            # Gestione dell'esito della partita
            if result == "quit_to_menu":
                quit_to_menu = True
                break  # Interrompe le partite correnti
            elif result is False:
                # Se il giocatore ha cliccato la X rossa per chiudere la finestra
                pygame.quit()
                sys.exit()

            play_count += 1

        # Se l'utente ha abbandonato con 'Q', il ciclo while True ricomincia dall'inizio
        if quit_to_menu:
            continue

        # Se tutte le partite sono state completate normalmente, usciamo
        break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()