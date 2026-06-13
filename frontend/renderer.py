import pygame
from config import *

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
    pygame.draw.rect(surf, colour, r, border_radius=5)
    pygame.draw.rect(surf, (40, 40, 50),
                     pygame.Rect(r.x + 4, r.y + 8, CAR_W - 8, CAR_H // 5), border_radius=3)
    for lx in (r.x + 2, r.right - 10):
        pygame.draw.rect(surf, (80, 80, 100), pygame.Rect(lx, r.bottom - 8, 8, 5), border_radius=2)

def draw_obstacle(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - OBS_W // 2, cy - OBS_H // 2, OBS_W, OBS_H)
    pygame.draw.rect(surf, colour, r, border_radius=4)
    m = 10
    pygame.draw.line(surf, (255, 255, 255), (r.x + m, r.y + m), (r.right - m, r.bottom - m), 2)
    pygame.draw.line(surf, (255, 255, 255), (r.right - m, r.y + m), (r.x + m, r.bottom - m), 2)

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

def draw_hud(surf: pygame.Surface, fonts: tuple, remaining: float,
             player_lane: int, collisions: int, avoidances: int) -> None:
    font_b, font, font_s = fonts
    
    # Header HUD
    pygame.draw.rect(surf, (10, 10, 15), (0, 0, WINDOW_W, 55))
    pygame.draw.line(surf, C_ACCENT, (0, 55), (WINDOW_W, 55), 2)

    # Timer
    mins, secs = divmod(int(remaining), 60)
    center_text(surf, f"{mins:02d}:{secs:02d}", font_b,
                C_WARNING if remaining < 15 else C_TEXT, 15)

    # Errori
    err_col = C_WARNING if collisions > 0 else (150, 150, 150)
    render_shadow_text(surf, f"ERR: {collisions}", font, err_col, (20, 18))

    # Precisione
    total = collisions + avoidances
    acc = (avoidances / total * 100) if total else 100.0
    acc_text = f"ACC: {acc:.0f}%"
    acc_surf = font.render(acc_text, True, C_ACCENT)
    render_shadow_text(surf, acc_text, font, C_ACCENT, (WINDOW_W - acc_surf.get_width() - 20, 18))

    # Indicatori corsia
    for lane, label in enumerate(("LEFT", "RIGHT")):
        col = C_ACCENT if lane == player_lane else (150, 150, 150)
        ls = font.render(label, True, col)
        pygame.draw.rect(surf, (0, 0, 0), (LANE_CENTERS[lane] - 35, surf.get_height() - 35, 70, 25), border_radius=4)
        surf.blit(ls, (LANE_CENTERS[lane] - ls.get_width() // 2, surf.get_height() - 32))

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