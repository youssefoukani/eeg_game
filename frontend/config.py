# ─── config.py ────────────────────────────────────────────────────────────────
import pygame
pygame.init()

_info      = pygame.display.Info()
WINDOW_W   = _info.current_w
WINDOW_H   = _info.current_h
FPS        = 60

# Session
MATCH_DURATION   = 5    # seconds
CROSS_DURATION   = 2.0   # seconds

# Lanes
LANE_LEFT  = 0
LANE_RIGHT = 1

# Obstacle timing
OBSTACLE_TRAVEL_TIME = 5   # seconds spawn → collision
SPAWN_MIN            = 18   # seconds between obstacles
SPAWN_MAX            = 20

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
C_WARNING      = (255, 160, 50)
C_OK           = (80,  210, 120)
C_HUD_BG       = (24,  24,  30)
C_DIVIDER      = (45,  45,  55)
C_INPUT_BG     = (28,  28,  36)
C_INPUT_ACTIVE = (40,  40,  55)
C_INPUT_BORDER = (60,  60,  80)
C_INPUT_SEL    = (60,  100, 180)
C_CUE = (0, 255, 0)

C_BG      = (20, 20, 20)      # Sfondo nero
C_TEXT    = (255, 255, 255)   # Testo bianco
C_MUTED   = (180, 180, 180)   # Grigio chiaro per i testi secondari
C_ACCENT  = (0, 200, 255)     # Azzurro per risaltare

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