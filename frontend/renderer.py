import pygame
from config import *
import random
import math


def make_fonts() -> tuple:
    """Return (font_bold, font, font_small) tuple using standard system fonts."""
    # Arial è molto più leggibile su monitor rispetto al monospace
    return (
        pygame.font.SysFont("arial", 25, bold=True),
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


def render_outline_text(surf: pygame.Surface, text: str, font, colour, pos, outline_colour=(0, 0, 0)):
    """Testo con outline a 4 direzioni: più leggibile su sfondi vari rispetto alla sola ombra."""
    x, y = pos
    outline = font.render(text, True, outline_colour)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(outline, (x + dx, y + dy))
    s = font.render(text, True, colour)
    surf.blit(s, (x, y))
    return s


def center_text(surf: pygame.Surface, text: str, font, colour, y: int, x: int = None) -> int:
    s = font.render(text, True, colour)
    bx = (x if x is not None else WINDOW_W // 2) - s.get_width() // 2
    render_outline_text(surf, text, font, colour, (bx, y))
    return s.get_height()


def divider(surf: pygame.Surface, y: int, margin: int = 60) -> None:
    """Disegna una linea divisoria."""
    pygame.draw.line(surf, C_DIVIDER, (margin, y), (WINDOW_W - margin, y), 1)


def _clamp_colour(colour) -> tuple:
    return tuple(min(255, max(0, int(c))) for c in colour)


def draw_car(surf: pygame.Surface, cx: float, cy: float, colour: tuple) -> None:
    r = pygame.Rect(cx - CAR_W // 2, cy - CAR_H // 2, CAR_W, CAR_H)

    # --- Ombra morbida con alpha reale (richiede una surface dedicata con SRCALPHA) ---
    pad = 6
    shadow_surf = pygame.Surface((CAR_W + pad * 2, CAR_H + pad * 2), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow_surf, (0, 0, 0, 70),
        pygame.Rect(pad, pad, CAR_W, CAR_H), border_radius=8
    )
    # leggero blur "povero" tramite scalatura down/up, costa pochissimo ed è efficace
    small = pygame.transform.smoothscale(shadow_surf, (max(1, (CAR_W + pad * 2) // 3), max(1, (CAR_H + pad * 2) // 3)))
    shadow_surf = pygame.transform.smoothscale(small, (CAR_W + pad * 2, CAR_H + pad * 2))
    surf.blit(shadow_surf, (r.x - pad + 3, r.y - pad + 5))

    # --- Corpo principale con gradiente verticale (chiaro in alto, scuro in basso) ---
    body_surf = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
    for i in range(CAR_H):
        t = i / CAR_H
        blend = _clamp_colour(c * (1.18 - t * 0.35) for c in colour)
        pygame.draw.line(body_surf, blend, (0, i), (CAR_W, i))
    # applica la forma arrotondata come maschera
    mask_surf = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
    pygame.draw.rect(mask_surf, (255, 255, 255, 255), mask_surf.get_rect(), border_radius=6)
    body_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body_surf, r.topleft)

    # Parabrezza (più scuro, leggermente trapezoidale)
    windshield = [
        (r.x + 6, r.y + CAR_H * 0.28),
        (r.right - 6, r.y + CAR_H * 0.28),
        (r.right - 10, r.y + CAR_H * 0.55),
        (r.x + 10, r.y + CAR_H * 0.55),
    ]
    pygame.draw.polygon(surf, (35, 40, 55), windshield)
    # piccolo riflesso diagonale sul parabrezza per dare lucentezza
    pygame.draw.line(surf, (90, 100, 130), (r.x + 9, r.y + CAR_H * 0.30), (r.x + 16, r.y + CAR_H * 0.30), 2)

    # Lunotto posteriore
    rear_window = pygame.Rect(r.x + 8, r.bottom - CAR_H // 4, CAR_W - 16, CAR_H // 6)
    pygame.draw.rect(surf, (40, 40, 50), rear_window, border_radius=2)

    # Fari anteriori (gialli/bianchi) con leggero glow
    for lx in (r.x + 3, r.right - 9):
        glow_rect = pygame.Rect(lx - 1, r.y + 1, 8, 7)
        glow = pygame.Surface((8, 7), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 240, 180, 90), glow.get_rect(), border_radius=3)
        surf.blit(glow, glow_rect.topleft)
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
    """Ostacolo stile 'lavori in corso': blocco unico con strisce gialle/nere.

    Tutta la grafica resta contenuta nel rettangolo di collisione `r`,
    quindi non ci sono parti (gambe, piedi, ecc.) che sporgono visivamente
    fuori dall'area che genera la collisione.

    Il parametro `colour` non è usato direttamente per il corpo (per restare
    fedele al tema cantiere), ma viene mantenuto in firma per compatibilità
    con le chiamate esistenti.
    """
    r = pygame.Rect(cx - OBS_W // 2, cy - OBS_H // 2, OBS_W, OBS_H)

    # Ombra leggera sotto il blocco (puramente estetica, non sporge sui lati)
    shadow_surf = pygame.Surface((r.width + 6, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
    surf.blit(shadow_surf, (r.x - 3, r.bottom - 4))

    # Corpo del blocco: base scura + pannello a strisce, tutto dentro r
    pygame.draw.rect(surf, (35, 35, 33), r, border_radius=6)

    panel = r.inflate(-6, -6)

    pygame.draw.rect(surf, (242, 194, 53), panel, border_radius=4)
    stripe_w = 8
    clip = surf.get_clip()
    surf.set_clip(panel)
    x = panel.x - panel.height
    i = 0
    while x < panel.right:
        if i % 2 == 1:
            pygame.draw.polygon(surf, (31, 31, 30), [
                (x, panel.bottom), (x + panel.height, panel.y),
                (x + panel.height + stripe_w, panel.y), (x + stripe_w, panel.bottom)
            ])
        x += stripe_w
        i += 1
    surf.set_clip(clip)

    pygame.draw.rect(surf, (20, 20, 20), panel, 3, border_radius=4)

    # Riflesso in alto per un filo di profondità
    pygame.draw.line(surf, (245, 245, 245), (panel.x + 4, panel.y + 2),
                      (panel.right - 4, panel.y + 2), 1)

    # Bordo esterno netto: coincide esattamente col rettangolo di collisione
    pygame.draw.rect(surf, (15, 15, 15), r, 2, border_radius=6)


def _pseudo_random(seed: int) -> float:
    """Numero deterministico in [0, 1) a partire da un intero. Usato per variare leggermente
    forma/colore di ogni albero senza che cambi ad ogni frame (deve restare stabile nel tempo,
    altrimenti la decorazione 'tremola' mentre scorre)."""
    seed = (seed * 9301 + 49297) % 233280
    return seed / 233280.0


# Tavolozza di verdi per le chiome: dal più scuro (base/ombra) al più chiaro (luce)
_FOLIAGE_GREENS = [
    (48, 92, 52),
    (62, 112, 60),
    (80, 134, 72),
    (100, 154, 82),
]


def _draw_tree(surf: pygame.Surface, x: float, y: float, scale: float = 1.0, seed: int = 0) -> None:
    """Albero con chioma 'a grappolo': più cerchi sovrapposti di verde diverso invece di
    un singolo cerchio piatto, per un risultato meno geometrico/finto."""
    rnd = _pseudo_random(seed)

    trunk_w, trunk_h = 10 * scale, 26 * scale
    trunk_x = x - trunk_w / 2

    # Ombra a terra (ellisse scura e morbida sotto la chioma)
    shadow_w, shadow_h = 46 * scale, 14 * scale
    shadow_surf = pygame.Surface((int(shadow_w), int(shadow_h)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (20, 30, 15, 70), shadow_surf.get_rect())
    surf.blit(shadow_surf, (x - shadow_w / 2, y + trunk_h - shadow_h * 0.4))

    # Tronco con leggera ombra laterale per dare volume
    pygame.draw.rect(surf, (96, 68, 42), pygame.Rect(trunk_x, y, trunk_w, trunk_h), border_radius=2)
    pygame.draw.rect(surf, (74, 52, 32), pygame.Rect(trunk_x, y, trunk_w * 0.35, trunk_h), border_radius=2)

    # Chioma: 5 cerchi sovrapposti, dal più grande/scuro dietro al più piccolo/chiaro davanti.
    # Le posizioni relative variano leggermente in base al seed, così alberi diversi non
    # sembrano fotocopie identiche, ma il risultato resta stabile frame dopo frame.
    cx, cy = x, y - 6 * scale
    base_r = 26 * scale
    blobs = [
        (0,            -base_r * 0.10, base_r * 1.00, _FOLIAGE_GREENS[0]),
        (-base_r * 0.62, base_r * 0.18, base_r * 0.68, _FOLIAGE_GREENS[1]),
        (base_r * 0.60,  base_r * 0.20, base_r * 0.66, _FOLIAGE_GREENS[1]),
        (-base_r * 0.18, -base_r * 0.55, base_r * 0.55, _FOLIAGE_GREENS[2]),
        (base_r * 0.30,  -base_r * 0.50, base_r * 0.46, _FOLIAGE_GREENS[3]),
    ]
    jitter = (rnd - 0.5) * base_r * 0.25
    for dx, dy, r, colour in blobs:
        pygame.draw.circle(surf, colour, (int(cx + dx + jitter), int(cy + dy)), max(2, int(r)))


def _draw_bush(surf: pygame.Surface, x: float, y: float, scale: float = 1.0, seed: int = 0) -> None:
    """Cespuglio: cluster di ellissi verdi sovrapposte invece di una singola forma piatta."""
    rnd = _pseudo_random(seed + 7)

    shadow_surf = pygame.Surface((int(44 * scale), int(12 * scale)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (20, 30, 15, 60), shadow_surf.get_rect())
    surf.blit(shadow_surf, (x - 22 * scale, y + 6 * scale))

    base_w, base_h = 26 * scale, 16 * scale
    jitter = (rnd - 0.5) * 6 * scale
    blobs = [
        (-12 * scale + jitter, 2 * scale, base_w, base_h, _FOLIAGE_GREENS[0]),
        (10 * scale - jitter,  3 * scale, base_w * 0.9, base_h * 0.85, _FOLIAGE_GREENS[1]),
        (0,                   -6 * scale, base_w * 0.8, base_h * 0.8, _FOLIAGE_GREENS[2]),
    ]
    for dx, dy, w, h, colour in blobs:
        pygame.draw.ellipse(surf, colour, pygame.Rect(x + dx - w / 2, y + dy - h / 2, w, h))




def draw_scenery(surf: pygame.Surface, scroll_offset: float) -> None:
    """Disegna lo sfondo decorativo: erba, guardrail, alberi/cespugli che scorrono in sincrono
    con la strada, e nuvole statiche in alto. Va chiamata PRIMA di draw_road, così resta
    sullo sfondo e non interferisce con collisioni o leggibilità del gameplay.

    `scroll_offset` deve essere lo stesso valore (o multiplo) usato per `dash_offset`
    in draw_road, per dare l'illusione che gli elementi laterali scorrano insieme alla strada.
    """
    h = surf.get_height()

    # Erba laterale (tono desaturato, non un verde acceso da prato sintetico)
    grass_colour = (118, 142, 96)
    pygame.draw.rect(surf, grass_colour, (0, 0, ROAD_X, h))
    pygame.draw.rect(surf, grass_colour, (ROAD_X + ROAD_W, 0, surf.get_width() - (ROAD_X + ROAD_W), h))

    # Guardrail lungo i bordi della carreggiata
    rail_w = 8
    pygame.draw.rect(surf, (168, 172, 176), (ROAD_X - rail_w - 4, 0, rail_w, h), border_radius=3)
    pygame.draw.rect(surf, (168, 172, 176), (ROAD_X + ROAD_W + 4, 0, rail_w, h), border_radius=3)

    # Alberi e cespugli a sinistra/destra, in loop verticale sincronizzato con la strada.
    #
    # IMPORTANTE: il tipo di decorazione (albero/cespuglio/variante) NON deve dipendere dal
    # contatore del while (quante righe sono visibili in QUESTO frame), perché quel numero
    # cambia ogni volta che una nuova riga entra dall'alto — e farebbe "cambiare tipo" alla
    # stessa riga mentre scorre. Usiamo un row_id calcolato dalla posizione assoluta nel
    # mondo (scroll_offset), stabile per una data riga indipendentemente da quante altre
    # sono visibili. Lo stesso row_id viene anche usato come seed per la variazione di forma,
    # così ogni "slot" ha sempre lo stesso aspetto nel tempo.
    cycle = 220
    off = scroll_offset % cycle
    left_x = max(30, ROAD_X - 55)
    right_x = min(surf.get_width() - 30, ROAD_X + ROAD_W + 55)

    y = -cycle + off
    while y < h:
        row_id = round((scroll_offset - y) / cycle)
        pattern = row_id % 3
        if pattern == 0:
            _draw_tree(surf, left_x, y, scale=1.3, seed=row_id * 2)
            _draw_bush(surf, right_x, y + 80, scale=1.2, seed=row_id * 2 + 1)
        elif pattern == 1:
            _draw_bush(surf, left_x - 12, y + 35, scale=1.1, seed=row_id * 2)
            _draw_tree(surf, right_x + 12, y, scale=1.15, seed=row_id * 2 + 1)
        else:
            _draw_tree(surf, left_x + 18, y + 55, scale=0.95, seed=row_id * 2)
            _draw_tree(surf, right_x - 10, y + 10, scale=1.05, seed=row_id * 2 + 1)
        y += cycle



def draw_road(surf: pygame.Surface, dash_offset: float) -> None:
    h = surf.get_height()
    pygame.draw.rect(surf, C_ROAD, (ROAD_X, 0, ROAD_W, h))

    # Bordi sfumati verso il marciapiede, invece di una linea netta
    edge_w = 12
    for i in range(edge_w):
        t = i / edge_w
        col = _clamp_colour(c - (1 - t) * 25 for c in C_LANE_DIV)
        pygame.draw.line(surf, col, (ROAD_X + i, 0), (ROAD_X + i, h))
        pygame.draw.line(surf, col, (ROAD_X + ROAD_W - i, 0), (ROAD_X + ROAD_W - i, h))

    # Linee di carreggiata nette sopra lo sfumato
    for x in (ROAD_X, ROAD_X + ROAD_W):
        pygame.draw.line(surf, C_LANE_DIV, (x, 0), (x, h), 2)

    # Linea centrale tratteggiata: rettangoli arrotondati invece di linee dure
    cx = ROAD_X + LANE_W
    dash_h, gap = 28, 16
    cycle = dash_h + gap
    y = -cycle + int(dash_offset) % cycle
    while y < h:
        pygame.draw.rect(surf, C_LANE_DIV, pygame.Rect(cx - 1, y, 3, dash_h), border_radius=2)
        y += cycle


def draw_button(surf: pygame.Surface, text: str, font, pos_center: tuple, padding: int = 20, hovered: bool = False) -> pygame.Rect:
    # 1. Renderizza il testo per calcolarne le dimensioni
    text_surf = font.render(text, True, (255, 255, 255))
    tw, th = text_surf.get_size()

    # 2. Crea il rettangolo dinamico centrato
    btn_rect = pygame.Rect(0, 0, tw + padding * 2, th + padding)
    btn_rect.center = pos_center

    # 3. Gestione colore flat (cambia solo la luminosità in hover)
    colour = _clamp_colour(c + 25 for c in C_ACCENT) if hovered else C_ACCENT

    # 4. Disegna lo sfondo del pulsante (pulito, senza ombre o linee 3D)
    pygame.draw.rect(surf, colour, btn_rect, border_radius=8)

    # 5. Centra e disegna il testo
    text_pos = (btn_rect.centerx - tw // 2, btn_rect.centery - th // 2)
    surf.blit(text_surf, text_pos)

    return btn_rect

def round_image(surface: pygame.Surface, radius: int) -> pygame.Surface:
    """Ritorna una copia della superficie con gli angoli smussati."""
    rect = surface.get_rect()
    # Crea una superficie di shape identica, inizialmente trasparente
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    
    # Disegna un rettangolo bianco pieno con gli angoli smussati sulla maschera
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=radius)
    
    # Copia l'immagine originale e usa il metodo BLEND_RGBA_MIN per ritagliarla
    image = surface.copy()
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return image