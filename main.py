# ─── main.py ──────────────────────────────────────────────────────────────────
# Entry point. Orchestrates the pre-game pipeline and the game loop.
#
# Pre-game pipeline:
#   1. UserDataForm        – participant registration
#   2. SignalQualityCheck  – EEG OSC connection + channel quality
#   3. FixationCross       – 2–5 s resting-state baseline
#   4. StartScreen         – instructions + SPACE to begin
#
# Run:
#   python main.py
#
# Requires:
#   pip install pygame python-osc

import sys
import pygame

from config import WINDOW_W, WINDOW_H
from eeg_interface import EEGInterface
from screens import UserDataForm, SignalQualityCheck, FixationCross, StartScreen
from game_engine import GameEngine


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("EEG BCI Runner — Motor Imagery Prototype")
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    # 1. Participant registration
    participant = UserDataForm(screen).run()

    # 2. EEG connection + signal quality (single instance reused throughout)
    eeg = EEGInterface()
    SignalQualityCheck(screen, eeg).run()

    # 3. Fixation cross baseline
    FixationCross(screen).run()

    # 4. Instruction screen
    StartScreen(screen, participant).run()

    # 5. Game loop (restart supported)
    while True:
        engine = GameEngine(screen, participant, eeg=eeg)
        if not engine.run():
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()