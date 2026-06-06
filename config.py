# ─── config.py ────────────────────────────────────────────────────────────────
# All tunable constants for the EEG BCI Runner.
# Change values here; nothing else needs to be touched.

# Window
WINDOW_W, WINDOW_H = 520, 700
FPS                = 60

# Session timing
MATCH_DURATION     = 120    # seconds (2 minutes)
FIXATION_MIN       = 2.0    # seconds – minimum fixation cross duration
FIXATION_MAX       = 5.0    # seconds – maximum fixation cross duration

# Lane identifiers
LANE_LEFT          = 0
LANE_RIGHT         = 1

# Obstacle timing
# Must be ≥ 2 s to cover EEG epoch + preprocessing + inference latency.
# Breakdown: ~2.0 s epoch | ~0.3 s filter | ~0.1 s inference | ~0.4 s margin
OBSTACLE_TRAVEL_TIME = 2.8  # seconds from spawn to collision line
SPAWN_MIN            = 2.5  # seconds between obstacles (min)
SPAWN_MAX            = 4.5  # seconds between obstacles (max)

# Road layout (pixels)
ROAD_X           = 110
ROAD_W           = 300
LANE_W           = ROAD_W // 2
LANE_CENTERS     = [ROAD_X + LANE_W // 2, ROAD_X + LANE_W + LANE_W // 2]
PLAYER_Y         = WINDOW_H - 130
OBSTACLE_SPAWN_Y = 60
OBSTACLE_HIT_Y   = PLAYER_Y - 10

# Sprite sizes (pixels)
CAR_W, CAR_H = 38, 70
OBS_W, OBS_H = 38, 50

# Colour palette (research-grade, minimal)
C_BG           = (18,  18,  22)
C_ROAD         = (30,  30,  36)
C_LANE_DIV     = (55,  55,  65)
C_PLAYER       = (220, 220, 230)
C_OBSTACLE     = (200, 60,  60)
C_OBSTACLE_HIT = (255, 80,  80)
C_TEXT         = (200, 200, 210)
C_MUTED        = (100, 100, 115)
C_ACCENT       = (80,  160, 255)
C_WARNING      = (255, 160, 50)
C_OK           = (80,  210, 120)
C_HUD_BG       = (24,  24,  30)
C_DIVIDER      = (45,  45,  55)
C_INPUT_BG     = (28,  28,  36)
C_INPUT_ACTIVE = (40,  40,  55)
C_INPUT_BORDER = (60,  60,  80)
C_INPUT_SEL    = (60,  100, 180)