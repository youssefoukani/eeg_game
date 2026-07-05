import pygame
import sys

def _handle_quit(ev):
    # Lasciamo solo l'evento QUIT (la X della finestra o il post() che abbiamo appena creato).
    # La gestione del tasto ESC è ora delegata alle singole schermate (come il tuo form).
    if ev.type == pygame.QUIT:
        pygame.quit()
        sys.exit()