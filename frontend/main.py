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
from screens import HeadsetGuide, UserDataForm, SignalQualityCheck, FixationCross, StartScreen
from game_engine import GameEngine


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("EEG BCI Runner — Motor Imagery Prototype")
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    participant = UserDataForm(screen).run()

    HeadsetGuide(screen).run()

    eeg = EEGInterface()
    SignalQualityCheck(screen, eeg).run()
    StartScreen(screen, participant).run()
    FixationCross(screen).run()

    while GameEngine(screen, participant, eeg=eeg).run():
        pass

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()