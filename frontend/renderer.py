import pygame
from config import *
import random
import math

def make_fonts() -> tuple:
    """Return (font_bold, font, font_small) tuple using standard system fonts."""
    # Arial è molto più leggibile su monitor rispetto al monospace
    return (
        pygame.font.SysFont("arial", 22, bold=True),
        pygame.font.SysFont("arial", 18),
        pygame.font.SysFont("arial", 16),
    )

def render_shadow_text(surf: pygame.Surface, text: str, font, colour, pos, shadow_colour=(0, 0, 0)):
    """Utility per disegnare testo con un'ombra per migliorare il contrasto."""
    shadow = font.render(text, True, shadow_colour)
    surf.blit(shadow, (pos[0] + 1, pos[1] + 1))
    s = font.render(text, True, colour)
    surf.blit(s, pos)
    return s

def center_text(surf: pygame.Surface, text: str, font, colour, y: int, x: int = None) -> int:
    s = font.render(text, True, colour)
    bx = (x if x is not None else WINDOW_W // 2) - s.get_width() // 2
    render_shadow_text(surf, text, font, colour, (bx, y))
    return s.get_height()

def divider(surf: pygame.Surface, y: int, margin: int = 60) -> None:
    """Disegna una linea divisoria."""
    pygame.draw.line(surf, C_DIVIDER, (margin, y), (WINDOW_W - margin, y), 1)

def draw_car(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - CAR_W // 2, cy - CAR_H // 2, CAR_W, CAR_H)

    # Ombra leggermente offset sotto l'auto, per dare profondità
    shadow = r.copy()
    shadow.move_ip(3, 5)
    pygame.draw.rect(surf, (0, 0, 0, 60), shadow, border_radius=6)

    # Corpo principale
    pygame.draw.rect(surf, colour, r, border_radius=6)
    # Leggero "sfumato" superiore per dare volume (striscia più chiara in alto)
    pygame.draw.rect(surf, tuple(min(c + 30, 255) for c in colour),
                      pygame.Rect(r.x, r.y, CAR_W, CAR_H // 4), border_radius=6)

    # Parabrezza (più scuro, leggermente trapezoidale)
    windshield = [
        (r.x + 6, r.y + CAR_H * 0.28),
        (r.right - 6, r.y + CAR_H * 0.28),
        (r.right - 10, r.y + CAR_H * 0.55),
        (r.x + 10, r.y + CAR_H * 0.55),
    ]
    pygame.draw.polygon(surf, (35, 40, 55), windshield)

    # Lunotto posteriore
    rear_window = pygame.Rect(r.x + 8, r.bottom - CAR_H // 4, CAR_W - 16, CAR_H // 6)
    pygame.draw.rect(surf, (40, 40, 50), rear_window, border_radius=2)

    # Fari anteriori (gialli/bianchi)
    for lx in (r.x + 3, r.right - 9):
        pygame.draw.rect(surf, (255, 240, 180), pygame.Rect(lx, r.y + 2, 6, 5), border_radius=2)

    # Stop posteriori (rossi)
    for lx in (r.x + 3, r.right - 9):
        pygame.draw.rect(surf, (200, 30, 30), pygame.Rect(lx, r.bottom - 7, 6, 5), border_radius=2)

    # Ruote ai lati (sporgenti dal corpo, viste dall'alto)
    wheel_w, wheel_h = 5, CAR_H // 4
    for wy in (r.y + CAR_H * 0.18, r.bottom - CAR_H * 0.18 - wheel_h):
        pygame.draw.rect(surf, (15, 15, 15), pygame.Rect(r.x - 2, wy, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surf, (15, 15, 15), pygame.Rect(r.right - wheel_w + 2, wy, wheel_w, wheel_h), border_radius=2)
        
def draw_obstacle(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - OBS_W // 2, cy - OBS_H // 2, OBS_W, OBS_H)
    pygame.draw.rect(surf, colour, r, border_radius=4)
    pygame.draw.rect(surf, (20, 20, 20), r, 2, border_radius=4)

    # Strisce diagonali rosse/gialle alternate (stile barriera di pericolo)
    stripe_w = 8
    clip = surf.get_clip()
    surf.set_clip(r)
    x = r.x - r.height
    i = 0
    while x < r.right:
        # Colori alternati: Rosso e Giallo
        colore_strip = (255, 0, 0) if i % 2 == 0 else (255, 255, 0)
        pygame.draw.polygon(surf, colore_strip, [
            (x, r.bottom), (x + r.height, r.y),
            (x + r.height + stripe_w, r.y), (x + stripe_w, r.bottom)
        ])
        x += stripe_w
        i += 1
    surf.set_clip(clip)
    
def draw_road(surf: pygame.Surface, dash_offset: float) -> None:
    pygame.draw.rect(surf, C_ROAD, (ROAD_X, 0, ROAD_W, surf.get_height()))
    for x in (ROAD_X, ROAD_X + ROAD_W):
        pygame.draw.line(surf, C_LANE_DIV, (x, 0), (x, surf.get_height()), 2)

    cx = ROAD_X + LANE_W
    dash_h, gap = 28, 16
    cycle = dash_h + gap
    y = -cycle + int(dash_offset) % cycle
    while y < surf.get_height():
        pygame.draw.line(surf, C_LANE_DIV, (cx, y), (cx, y + dash_h), 1)
        y += cycle

def draw_button(surf: pygame.Surface, text: str, font, pos_center: tuple, padding: int = 20) -> pygame.Rect:
    # Renderizza il testo per misurarlo
    text_surf = font.render(text, True, (255, 255, 255))
    tw, th = text_surf.get_size()
    
    # Crea il rettangolo dinamico
    btn_rect = pygame.Rect(0, 0, tw + padding * 2, th + padding)
    btn_rect.center = pos_center
    
    # Disegna il rettangolo (sfondo)
    pygame.draw.rect(surf, C_ACCENT, btn_rect, border_radius=8)
    
    # Centra il testo dentro il rettangolo
    surf.blit(text_surf, (btn_rect.centerx - tw // 2, btn_rect.centery - th // 2))
    
    return btn_rect