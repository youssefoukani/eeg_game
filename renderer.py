# ─── renderer.py ──────────────────────────────────────────────────────────────
# Stateless drawing helpers used by screens and the game engine.

import pygame
from config import (
    WINDOW_W, CAR_W, CAR_H, OBS_W, OBS_H,
    C_TEXT, C_MUTED, C_ACCENT, C_WARNING, C_OK,
    C_HUD_BG, C_DIVIDER, C_ROAD, C_LANE_DIV,
    C_OBSTACLE, C_OBSTACLE_HIT,
    ROAD_X, ROAD_W, LANE_W, LANE_CENTERS,
    OBSTACLE_HIT_Y,
)


# ── fonts ─────────────────────────────────────────────────────────────────────

def make_fonts() -> tuple:
    """Return (font_bold, font, font_small) monospace tuple."""
    return (
        pygame.font.SysFont("monospace", 17, bold=True),
        pygame.font.SysFont("monospace", 15),
        pygame.font.SysFont("monospace", 13),
    )


# ── generic helpers ───────────────────────────────────────────────────────────

def center_text(surf: pygame.Surface, text: str, font, colour: tuple,
                y: int, x: int | None = None) -> int:
    """Blit horizontally centred text; return surface height."""
    s  = font.render(text, True, colour)
    bx = (x if x is not None else WINDOW_W // 2) - s.get_width() // 2
    surf.blit(s, (bx, y))
    return s.get_height()


def divider(surf: pygame.Surface, y: int, margin: int = 60) -> None:
    pygame.draw.line(surf, C_DIVIDER, (margin, y), (WINDOW_W - margin, y), 1)


# ── game sprites ──────────────────────────────────────────────────────────────

def draw_car(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - CAR_W // 2, cy - CAR_H // 2, CAR_W, CAR_H)
    pygame.draw.rect(surf, colour, r, border_radius=5)

    # Windshield
    pygame.draw.rect(
        surf, (40, 40, 50),
        pygame.Rect(r.x + 4, r.y + 8, CAR_W - 8, CAR_H // 5),
        border_radius=3,
    )
    # Tail-lights
    ll_w, ll_h = 8, 5
    for lx in (r.x + 2, r.right - ll_w - 2):
        pygame.draw.rect(
            surf, (80, 80, 100),
            pygame.Rect(lx, r.bottom - ll_h - 3, ll_w, ll_h),
            border_radius=2,
        )


def draw_obstacle(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - OBS_W // 2, cy - OBS_H // 2, OBS_W, OBS_H)
    pygame.draw.rect(surf, colour, r, border_radius=4)
    m = 10
    pygame.draw.line(surf, (255, 255, 255),
                     (r.x + m, r.y + m), (r.right - m, r.bottom - m), 2)
    pygame.draw.line(surf, (255, 255, 255),
                     (r.right - m, r.y + m), (r.x + m, r.bottom - m), 2)


# ── road ──────────────────────────────────────────────────────────────────────

def draw_road(surf: pygame.Surface, dash_offset: float) -> None:
    pygame.draw.rect(surf, C_ROAD, (ROAD_X, 0, ROAD_W, surf.get_height()))
    pygame.draw.line(surf, C_LANE_DIV, (ROAD_X, 0), (ROAD_X, surf.get_height()), 2)
    pygame.draw.line(surf, C_LANE_DIV,
                     (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, surf.get_height()), 2)

    cx        = ROAD_X + LANE_W
    dash_h, gap = 28, 16
    cycle     = dash_h + gap
    y         = -cycle + int(dash_offset) % cycle
    while y < surf.get_height():
        pygame.draw.line(surf, C_LANE_DIV, (cx, y), (cx, y + dash_h), 1)
        y += cycle


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surf: pygame.Surface, fonts: tuple,
             remaining: float, player_lane: int,
             collisions: int, avoidances: int,
             events: list, obstacles: list) -> None:

    font_b, font, font_s = fonts
    h = surf.get_height()

    # Top bar
    pygame.draw.rect(surf, C_HUD_BG, (0, 0, WINDOW_W, 50))
    pygame.draw.line(surf, C_DIVIDER, (0, 50), (WINDOW_W, 50), 1)

    mins, secs  = int(remaining) // 60, int(remaining) % 60
    timer_col   = C_WARNING if remaining < 15 else C_TEXT
    center_text(surf, f"{mins:02d}:{secs:02d}", font_b, timer_col, 14)

    err_s = font.render(f"ERR {collisions}", True,
                        C_WARNING if collisions > 0 else C_MUTED)
    surf.blit(err_s, (20, 17))

    total   = collisions + avoidances
    acc_val = (avoidances / total * 100) if total else 100.0
    acc_s   = font.render(f"ACC {acc_val:.0f}%", True, C_ACCENT)
    surf.blit(acc_s, (WINDOW_W - acc_s.get_width() - 20, 17))

    # Lane labels (bottom)
    for i, label in enumerate(["LEFT", "RIGHT"]):
        col = C_ACCENT if player_lane == i else C_MUTED
        ls  = font_s.render(label, True, col)
        pygame.draw.rect(surf, C_HUD_BG, (LANE_CENTERS[i] - 28, h - 32, 56, 22))
        surf.blit(ls, (LANE_CENTERS[i] - ls.get_width() // 2, h - 29))

    # Event log (right panel)
    px, sy = ROAD_X + ROAD_W + 16, 70
    surf.blit(font_s.render("EVENT LOG", True, C_MUTED), (px, sy)); sy += 22
    pygame.draw.line(surf, C_DIVIDER, (px, sy), (px + 90, sy), 1);  sy += 8
    TAG_COLOUR = {"collision": (C_WARNING, "HIT"),
                  "avoidance": (C_ACCENT,  "OK "),
                  "lane_change": (C_MUTED, ">>>")}
    for ev in reversed(events[-4:]):
        col, tag = TAG_COLOUR[ev.event_type]
        surf.blit(font_s.render(f"{tag} t={ev.timestamp:5.1f}s", True, col), (px, sy))
        sy += 20

    # Incoming panel (left panel)
    px2, sy2 = 16, 70
    surf.blit(font_s.render("INCOMING", True, C_MUTED), (px2, sy2)); sy2 += 22
    pygame.draw.line(surf, C_DIVIDER, (px2, sy2), (px2 + 90, sy2), 1); sy2 += 8
    for obs in sorted([o for o in obstacles if not o.hit],
                      key=lambda o: o.y, reverse=True)[:3]:
        t_left   = max(0.0, (OBSTACLE_HIT_Y - obs.y) / obs.speed)
        lane_lbl = "L" if obs.lane == 0 else "R"
        col      = C_WARNING if t_left < 1.0 else C_TEXT
        surf.blit(font_s.render(f"[{lane_lbl}] {t_left:.1f}s", True, col), (px2, sy2))
        sy2 += 20