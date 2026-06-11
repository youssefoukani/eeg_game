import pygame
import sys

def _handle_quit(ev):

    if ev.type == pygame.QUIT or (
        ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE
    ):

        pygame.quit()
        sys.exit()