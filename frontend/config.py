# ─── config.py ────────────────────────────────────────────────────────────────
import pygame
pygame.init()

_info      = pygame.display.Info()
WINDOW_W   = _info.current_w
WINDOW_H   = _info.current_h
FPS        = 60

# Session
MATCH_DURATION   = 15   # seconds
CROSS_DURATION   = 2.0   # seconds

# Lanes
LANE_LEFT  = 0
LANE_RIGHT = 1

# Obstacle timing
OBSTACLE_TRAVEL_TIME = 5   # seconds spawn → collision
SPAWN_MIN            = 20  # seconds between obstacles
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


# ── Geometry ─────────────────────────────────────────────────────────────
RADIUS_SM   = 6
RADIUS_MD   = 8
FIELD_H     = 38
GAP_LABEL   = 8     # space between label and its control
GAP_FIELD   = 26    # space between one field group and the next
BORDER_W    = 1
FOCUS_RING_W = 2
 

FOOTER_Y = int(WINDOW_H * 0.80)

HEADER_Y = int(WINDOW_H * 0.1)


DAY_THEME = {
    "C_BG":            (220, 230, 242),   # Azzurro polvere/pastello (morbido, non stanca gli occhi)
    "C_BG_PANEL":      (248, 249, 252),   # Bianco sporco freddo per le card
    "C_ROAD":          (74, 80, 92),      # Grigio asfalto scuro bilanciato
    "C_LANE_DIV":      (235, 240, 245),   # Linee di corsia chiare e nitide
    "C_PLAYER":        (255, 255, 255),   # Bianco puro per far risaltare il giocatore
    "C_OBSTACLE":      (225, 85, 85),     # Rosso corallo moderno (meno aggressivo del puro)
    "C_OBSTACLE_HIT":  (245, 130, 130),   # Rosso chiaro per l'impatto
    "C_OK":            (46, 184, 114),    # Verde smeraldo per gli stati OK
    "C_WARNING":       (225, 95, 80),     # Arancio-rosso di avviso
    "C_HUD_BG":        (240, 244, 248),   # Sfondo HUD leggermente azzurrato per coerenza
    "C_DIVIDER":       (195, 205, 215),   # Linee di divisione pulite e desaturate
    "C_TEXT":          (40, 48, 64),      # Blu notte scurissimo (sostituisce il nero puro, molto più moderno)
    "C_MUTED":         (100, 112, 132),   # Grigio-blu medio per testi secondari
    "C_FAINT":         (160, 172, 190),   # Grigio chiaro per dettagli sottili
    "C_ACCENT":        (54, 134, 232),    # Blu elettrico brillante per bottoni e focus
    "C_ACCENT_DIM":    (38, 106, 194),    # Blu scuro per stati hover/premuti
    "C_ACCENT_GLOW":   (54, 134, 232, 40),# Glow semitrasparente
    "C_INPUT_BG":      (240, 243, 247),   # Sfondo input integrato con la palette
    "C_INPUT_ACTIVE":  (228, 234, 242),   # Sfondo quando l'input è attivo
    "C_INPUT_BORDER":  (180, 192, 208),   # Bordo neutro
    "C_INPUT_SEL":     (54, 134, 232),    # Sezione selezionata coerente con l'accento
    "C_SUCCESS":       (46, 184, 114),    # Verde successo coordinato
    "C_PENDING":       (242, 160, 60),    # Giallo ambra caldo
    "C_CUE":           (30, 190, 120),    # Indicatore EEG visibile ma pulito
    "C_BORDEAUX":      (150, 40, 75),     # Bordeaux leggermente più morbido
}


NIGHT_THEME = {

    "C_BG":            (22, 24, 32),

    "C_BG_PANEL":      (34, 38, 52),

    "C_ROAD":          (52, 56, 70),

    "C_LANE_DIV":      (150, 160, 180),

    "C_PLAYER":        (248, 248, 255),

    "C_OBSTACLE":      (255, 95, 95),

    "C_OBSTACLE_HIT":  (255, 140, 140),

    "C_OK":            (70, 225, 120),

    "C_WARNING":       (200, 70, 70),

    "C_HUD_BG":        (30, 34, 46),

    "C_DIVIDER":       (70, 78, 98),

    "C_TEXT":          (250, 250, 255),

    "C_MUTED":         (185, 192, 208),

    "C_FAINT":         (120, 128, 145),

    "C_ACCENT":        (70, 170, 255),

    "C_ACCENT_DIM":    (50, 120, 220),

    "C_ACCENT_GLOW":   (70, 170, 255, 50),

    "C_INPUT_BG":      (40, 45, 60),

    "C_INPUT_ACTIVE":  (55, 63, 82),

    "C_INPUT_BORDER":  (95, 105, 130),

    "C_INPUT_SEL":     (70, 125, 215),

    "C_SUCCESS":       (70, 225, 120),

    "C_PENDING":       (255, 195, 75),

    "C_CUE":           (0, 255, 120),

    "C_BORDEAUX":      (170, 45, 85),

}

THEME = NIGHT_THEME.copy()

def set_theme(dark):

    THEME.clear()

    THEME.update(NIGHT_THEME if dark else DAY_THEME)