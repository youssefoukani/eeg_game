# ─── config.py ────────────────────────────────────────────────────────────────
import pygame
pygame.init()

_info      = pygame.display.Info()
WINDOW_W   = _info.current_w
WINDOW_H   = _info.current_h
FPS        = 60

# Session
MATCH_DURATION   = 180   # seconds
CROSS_DURATION   = 2.0   # seconds

# Lanes
LANE_LEFT  = 0
LANE_RIGHT = 1

# Obstacle timing
OBSTACLE_TRAVEL_TIME = 5   # seconds spawn → collision
SPAWN_MIN            = 20   # seconds between obstacles
SPAWN_MAX            = 20
CUE_LEAD_TIME = 5

# Road layout
ROAD_W       = WINDOW_W // 3
ROAD_X       = WINDOW_W // 3
PLAYER_Y     = WINDOW_H * 4 // 5
LANE_W       = ROAD_W // 2
LANE_CENTERS = [ROAD_X + LANE_W // 2, ROAD_X + LANE_W + LANE_W // 2]


# Sprites
CAR_W, CAR_H = 38, 70
OBS_W, OBS_H = int(CAR_W * 3), int(CAR_H * 1.2)

OBSTACLE_SPAWN_Y = 60
OBSTACLE_HIT_Y   = PLAYER_Y - CAR_H

# Colours
C_ROAD         = (30,  30,  36)
C_LANE_DIV     = (55,  55,  65)
C_PLAYER       = (220, 220, 230)
C_OBSTACLE     = (200, 60,  60)
C_OBSTACLE_HIT = (255, 80,  80)
C_OK           = (80,  210, 120)
C_HUD_BG       = (24,  24,  30)
C_DIVIDER      = (45,  45,  55)
C_INPUT_BG     = (28,  28,  36)
C_INPUT_ACTIVE = (40,  40,  55)
C_INPUT_BORDER = (60,  60,  80)
C_INPUT_SEL    = (60,  100, 180)
C_CUE = (0, 255, 0)
C_BORDEAUX = (128, 0, 32)



FONT_MAIN = "arial" 
FONT_CODE = "consolas"

# Definizione dimensioni (Small, Medium, Large, Header)
SIZE_XS   = 12
SIZE_S    = 16
SIZE_M    = 20
SIZE_L    = 28
SIZE_XL   = 40

# --- UI CONSTANTS ---
BORDER_RADIUS = 8

# ── Palette ──────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────

# Base Colors

# ─────────────────────────────────────────────────────────────

C_BG            = (22, 24, 32)

C_BG_PANEL      = (34, 38, 52)

C_ROAD          = (52, 56, 70)

C_LANE_DIV      = (145, 155, 175)

C_PLAYER        = (248, 248, 255)

C_OBSTACLE      = (255, 95, 95)

C_OBSTACLE_HIT  = (255, 140, 140)

C_OK            = (70, 225, 120)

C_WARNING       = (255, 180, 70)

C_HUD_BG        = (30, 34, 46)

C_DIVIDER       = (70, 78, 98)

# ─────────────────────────────────────────────────────────────

# Text

# ─────────────────────────────────────────────────────────────

C_TEXT          = (250, 250, 255)

C_MUTED         = (185, 192, 208)

C_FAINT         = (120, 128, 145)

# ─────────────────────────────────────────────────────────────

# Accent

# ─────────────────────────────────────────────────────────────

C_ACCENT        = (70, 170, 255)

C_ACCENT_DIM    = (50, 120, 220)

C_ACCENT_GLOW   = (70, 170, 255, 50)

# ─────────────────────────────────────────────────────────────

# Input

# ─────────────────────────────────────────────────────────────

C_INPUT_BG      = (40, 45, 60)

C_INPUT_ACTIVE  = (55, 63, 82)

C_INPUT_BORDER  = (95, 105, 130)

C_INPUT_SEL     = (70, 125, 215)

# ─────────────────────────────────────────────────────────────

# Feedback

# ─────────────────────────────────────────────────────────────

C_SUCCESS       = (70, 225, 120)

C_PENDING       = (255, 195, 75)

C_CUE           = (60, 255, 120)

C_BORDEAUX      = (170, 45, 85)
# ── Geometry ─────────────────────────────────────────────────────────────
RADIUS_SM   = 6
RADIUS_MD   = 8
FIELD_H     = 38
GAP_LABEL   = 8     # space between label and its control
GAP_FIELD   = 26    # space between one field group and the next
BORDER_W    = 1
FOCUS_RING_W = 2
 

FOOTER_Y = 800