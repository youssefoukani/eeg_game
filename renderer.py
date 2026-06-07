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
#funzione helper per creare i font, così da non doverlo fare in ogni classe in screens.py e game_engine
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

def draw_hud(
    surf: pygame.Surface,
    fonts: tuple,
    remaining: float,
    player_lane: int,
    collisions: int,
    avoidances: int
) -> None:

    font_b, font, font_s = fonts
    h = surf.get_height()

    # Barra superiore
    pygame.draw.rect(surf, C_HUD_BG, (0, 0, WINDOW_W, 50))
    pygame.draw.line(surf, C_DIVIDER, (0, 50), (WINDOW_W, 50), 1)

    mins, secs = int(remaining) // 60, int(remaining) % 60
    timer_col = C_WARNING if remaining < 15 else C_TEXT

    center_text(
        surf,
        f"{mins:02d}:{secs:02d}",
        font_b,
        timer_col,
        14
    )

    err_s = font.render(
        f"ERR {collisions}",
        True,
        C_WARNING if collisions > 0 else C_MUTED
    )
    surf.blit(err_s, (20, 17))

    total = collisions + avoidances
    acc = (avoidances / total * 100) if total else 100.0

    acc_s = font.render(
        f"ACC {acc:.0f}%",
        True,
        C_ACCENT
    )
    surf.blit(
        acc_s,
        (WINDOW_W - acc_s.get_width() - 20, 17)
    )

    # Indicatori corsia
    for lane, label in enumerate(["LEFT", "RIGHT"]):

        color = C_ACCENT if lane == player_lane else C_MUTED

        label_surface = font_s.render(
            label,
            True,
            color
        )

        pygame.draw.rect(
            surf,
            C_HUD_BG,
            (LANE_CENTERS[lane] - 28, h - 32, 56, 22)
        )

        surf.blit(
            label_surface,
            (
                LANE_CENTERS[lane] - label_surface.get_width() // 2,
                h - 29
            )
        )