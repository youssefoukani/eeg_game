# ─── config.py ────────────────────────────────────────────────────────────────
import pygame
pygame.init()

_info      = pygame.display.Info()
WINDOW_W   = _info.current_w
WINDOW_H   = _info.current_h
FPS        = 60

# Session
MATCH_DURATION   = 60   # seconds
CROSS_DURATION   = 5.0   # seconds

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
    "C_BG":            (220, 230, 242),   # Azzurro pastello
    "C_BG_PANEL":      (248, 249, 252),   # Bianco freddo per le card
    "C_ROAD":          (74, 80, 92),      # Grigio asfalto scuro bilanciato
    "C_LANE_DIV":      (235, 240, 245),   # Linee di corsia chiare e nitide
    "C_PLAYER":        (255, 255, 255),   # Bianco puro per far risaltare il giocatore
    "C_OBSTACLE":      (225, 85, 85),     # Rosso corallo moderno
    "C_OBSTACLE_HIT":  (245, 130, 130),   # Rosso chiaro per l'impatto
    "C_OK":            (46, 184, 114),    # Verde smeraldo per gli stati OK
    "C_WARNING":       (225, 95, 80),     # Arancio-rosso di avviso
    "C_HUD_BG":        (240, 244, 248),   # Sfondo HUD leggermente azzurrato per coerenza
    "C_DIVIDER":       (195, 205, 215),   # Linee di divisione pulite e desaturate
    "C_TEXT":          (40, 48, 64),      # Blu notte scurissimo
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
    "C_BORDEAUX":      (150, 40, 75),    
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

# ── Esposizione dei colori come variabili di modulo ─────────────────────────
# ATTENZIONE — snapshot congelato, NON live: queste variabili vengono copiate
# per valore da ogni file che fa `from config import *`, quindi restano
# ferme al tema in vigore al momento dell'import e NON seguono set_theme()/
# toggle_theme() chiamati a runtime. Sono qui solo per compatibilità con
# eventuali file non ancora convertiti al lookup live THEME["C_X"] (usato
# invece da renderer.py e da tutte le schermate principali per supportare
# il cambio tema a caldo).

C_BG           = THEME["C_BG"]
C_BG_PANEL     = THEME["C_BG_PANEL"]
C_ROAD         = THEME["C_ROAD"]
C_LANE_DIV     = THEME["C_LANE_DIV"]
C_PLAYER       = THEME["C_PLAYER"]
C_OBSTACLE     = THEME["C_OBSTACLE"]
C_OBSTACLE_HIT = THEME["C_OBSTACLE_HIT"]
C_OK           = THEME["C_OK"]
C_WARNING      = THEME["C_WARNING"]
C_HUD_BG       = THEME["C_HUD_BG"]
C_DIVIDER      = THEME["C_DIVIDER"]
C_TEXT         = THEME["C_TEXT"]
C_MUTED        = THEME["C_MUTED"]
C_FAINT        = THEME["C_FAINT"]
C_ACCENT       = THEME["C_ACCENT"]
C_ACCENT_DIM   = THEME["C_ACCENT_DIM"]
C_ACCENT_GLOW  = THEME["C_ACCENT_GLOW"]
C_INPUT_BG     = THEME["C_INPUT_BG"]
C_INPUT_ACTIVE = THEME["C_INPUT_ACTIVE"]
C_INPUT_BORDER = THEME["C_INPUT_BORDER"]
C_INPUT_SEL    = THEME["C_INPUT_SEL"]
C_SUCCESS      = THEME["C_SUCCESS"]
C_PENDING      = THEME["C_PENDING"]
C_CUE          = THEME["C_CUE"]
C_BORDEAUX     = THEME["C_BORDEAUX"]

globals().update(THEME)

def set_theme(dark):

    THEME.clear()

    THEME.update(NIGHT_THEME if dark else DAY_THEME)

    # Riallinea sia le assegnazioni esplicite sia la rete di sicurezza.
    # ATTENZIONE: i file che hanno già fatto `from config import *` prima
    # di questa chiamata hanno copiato i vecchi valori per valore e NON
    # si aggiornano da soli — set_theme() va quindi chiamato prima di
    # importare/istanziare le schermate, non a metà sessione.
    global C_BG, C_BG_PANEL, C_ROAD, C_LANE_DIV, C_PLAYER, C_OBSTACLE, \
        C_OBSTACLE_HIT, C_OK, C_WARNING, C_HUD_BG, C_DIVIDER, C_TEXT, \
        C_MUTED, C_FAINT, C_ACCENT, C_ACCENT_DIM, C_ACCENT_GLOW, C_INPUT_BG, \
        C_INPUT_ACTIVE, C_INPUT_BORDER, C_INPUT_SEL, C_SUCCESS, C_PENDING, \
        C_CUE, C_BORDEAUX

    C_BG           = THEME["C_BG"]
    C_BG_PANEL     = THEME["C_BG_PANEL"]
    C_ROAD         = THEME["C_ROAD"]
    C_LANE_DIV     = THEME["C_LANE_DIV"]
    C_PLAYER       = THEME["C_PLAYER"]
    C_OBSTACLE     = THEME["C_OBSTACLE"]
    C_OBSTACLE_HIT = THEME["C_OBSTACLE_HIT"]
    C_OK           = THEME["C_OK"]
    C_WARNING      = THEME["C_WARNING"]
    C_HUD_BG       = THEME["C_HUD_BG"]
    C_DIVIDER      = THEME["C_DIVIDER"]
    C_TEXT         = THEME["C_TEXT"]
    C_MUTED        = THEME["C_MUTED"]
    C_FAINT        = THEME["C_FAINT"]
    C_ACCENT       = THEME["C_ACCENT"]
    C_ACCENT_DIM   = THEME["C_ACCENT_DIM"]
    C_ACCENT_GLOW  = THEME["C_ACCENT_GLOW"]
    C_INPUT_BG     = THEME["C_INPUT_BG"]
    C_INPUT_ACTIVE = THEME["C_INPUT_ACTIVE"]
    C_INPUT_BORDER = THEME["C_INPUT_BORDER"]
    C_INPUT_SEL    = THEME["C_INPUT_SEL"]
    C_SUCCESS      = THEME["C_SUCCESS"]
    C_PENDING      = THEME["C_PENDING"]
    C_CUE          = THEME["C_CUE"]
    C_BORDEAUX     = THEME["C_BORDEAUX"]

    globals().update(THEME)


def is_dark_theme() -> bool:
    """True se il tema attivo è quello notturno. Va sempre chiamata (mai
    salvata in una variabile locale a lungo termine): legge THEME["C_BG"]
    al momento della chiamata e lo confronta con NIGHT_THEME, quindi resta
    corretta anche subito dopo un toggle_theme()."""
    return THEME.get("C_BG") == NIGHT_THEME["C_BG"]


def toggle_theme() -> None:
    """Alterna chiaro/scuro. Muta THEME in place tramite set_theme(), quindi
    ogni schermata che legge i colori con THEME["C_X"] (invece delle
    variabili piatte C_X) vede il cambiamento all'istante, senza dover
    ricaricare né riavviare nulla."""
    set_theme(dark=not is_dark_theme())