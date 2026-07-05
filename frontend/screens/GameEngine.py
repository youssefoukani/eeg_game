# ─── game_engine.py ───────────────────────────────────────────────────────────
import math
import time
import pygame

from config import *
from models import ParticipantData
from eeg_interface import EEGInterface
from input_manager import InputManager
from game_logic import PlayerController, ObstacleManager, CollisionSystem
from metrics_logger import MetricsLogger
from renderer import make_fonts, draw_car, draw_obstacle, draw_road, draw_scenery
from screens import ResultsScreen
from renderer import center_text

class GameEngine:
    """Runs one session. Returns True if the user requests a restart."""

    def __init__(self, screen: pygame.Surface, participant: ParticipantData, eeg: EEGInterface = None):
        self._screen      = screen
        self._participant = participant
        self._eeg         = eeg or EEGInterface()
        self._fonts       = make_fonts()
        self.label_font = pygame.font.SysFont("Montserrat", 72, bold=True)
        self.arrow_label_font = pygame.font.SysFont("Montserrat", 24, bold=False)
        self.is_paused = False
        self.pause_start_time = 0
        self.PAUSE_DURATION = 5  # secondi di pausa
        self.snapshot = None
        self.input_lock_until = 0
        self.feedback_text = ""

        # Font piccolo e discreto per l'indicatore di stato EEG
        self.eeg_font = pygame.font.SysFont("Montserrat", 16, bold=True)

    def run(self) -> bool:
        input_mgr  = InputManager(self._eeg, use_keyboard=True)
        player     = PlayerController()
        obstacles  = ObstacleManager()
        collisions = CollisionSystem()
        metrics    = MetricsLogger()

        clock         = pygame.time.Clock()
        session_start = time.time()
        dash_offset   = 0.0
        self.feedback_until = 0.0
        obs_speed     = (OBSTACLE_HIT_Y - OBSTACLE_SPAWN_Y) / OBSTACLE_TRAVEL_TIME


        while True:

            dt        = clock.tick(FPS) / 1000.0
            game_time = time.time() - session_start
            remaining = max(0.0, MATCH_DURATION - game_time)

            events = pygame.event.get()


            for ev in events:

                if ev.type == pygame.QUIT:

                    return False

                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:

                    return False

            if self.is_paused:
                # 1. Ripristina lo stato del gioco (cancella il timer precedente)
                self._screen.blit(self.snapshot, (0, 0))
                
                # 2. Calcola e disegna il nuovo timer
                tempo_rimanente = max(0, self.PAUSE_DURATION - (time.time() - self.pause_start_time))
                lines = [
                        "COLLISIONE!",
                        f"RESTART IN: {tempo_rimanente:.1f}"
                    ]
                    
                    # 4. Rendering multiriga centrato
                line_spacing = 10
                y = self._screen.get_height() // 2 - 40  # Offset iniziale per centrare il blocco
                
                for line in lines:
                    text_surface = self.label_font.render(line, True, (128, 0, 32))
                    text_rect = text_surface.get_rect(center=(self._screen.get_width() // 2, y))
                    self._screen.blit(text_surface, text_rect)
                    y += text_surface.get_height() + line_spacing

                # Anche durante la pausa il sistema resta "in ascolto":
                # mostriamo comunque l'indicatore per non far pensare
                # a un blocco del software.
                self.draw_eeg_status()

                pygame.display.flip()

                if time.time() - self.pause_start_time >= self.PAUSE_DURATION:
                    # 1. Determina la nuova corsia in modo deterministico
                    # Esempio: se è a sinistra, vai a destra, e viceversa.
                    # Assicurati che LANE_LEFT e LANE_RIGHT siano costanti univoche (es. 0 e 1)
                    target_lane = LANE_RIGHT if player.lane == LANE_LEFT else LANE_LEFT
                    
                    # 2. Aggiorna il controller del giocatore
                    player.move_to_lane_after_collision(target_lane)
                    
                    # 3. Aggiornamento FORZATO (senza interpolazione)
                    

                    
                    # 4. Feedback e reset stato
                    self.feedback_text = "READY!"
                    self.feedback_until = time.time() + 1.0
                    self.is_paused = False
                    self.input_lock_until = time.time() + 1.5
                    
                    # IMPORTANTE: Svuota la coda degli eventi per evitare che un tasto
                    # premuto durante la pausa causi un cambio corsia immediato appena riparte
                    pygame.event.clear()
                else:
                    continue

            if not self.is_paused:
                # --- LOGICA NORMALE ---
                
                # Verifica se siamo nel periodo di lock
                can_accept_input = time.time() > self.input_lock_until
                
                if can_accept_input:
                    input_mgr.poll(events)
                    cmd = input_mgr.get_player_command()
                    if cmd and player.apply_command(cmd):
                        metrics.log_lane_change(game_time, player.lane)
                else:
                    # Anche se bloccato, svuota la coda per evitare "accumulo"
                    pygame.event.clear()

                player.update()

                if remaining > 0:
                    obstacles.update(game_time, dt)

                dash_offset += obs_speed * dt
                self._screen.fill(C_BG)
                draw_scenery(self._screen, dash_offset)
                draw_road(self._screen, dash_offset)
                for obs in obstacles.obstacles:
                    if obs.visible:
                        draw_obstacle(self._screen, LANE_CENTERS[obs.lane], obs.y,
                                    C_OBSTACLE_HIT if obs.hit else C_OBSTACLE)
                draw_car(self._screen, player.x, PLAYER_Y, C_PLAYER)

                # FIX: il check va eseguito ad ogni frame (non solo a player
                # fermo), altrimenti un ostacolo evitato durante un cambio
                # corsia in corso può generare una collisione "fantasma" se
                # il player torna in quella corsia da fermo prima che
                # l'ostacolo venga rimosso. Con il check continuo, una volta
                # superata la finestra di sovrapposizione verticale senza
                # mai aver toccato l'auto, l'ostacolo resta hit=False per
                # sempre (CollisionSystem.check ignora gli obs già hit=True).
                hits = collisions.check(player, obstacles.obstacles, game_time)
                if hits:
                    obs = hits[0]
                    metrics.log_collision(game_time, player.lane, obs)
                    self.is_paused = True
                    self.pause_start_time = time.time()
                    self.snapshot = self._screen.copy()
                    continue

                for obs in obstacles.remove_passed():

                    print(
                        f"PASSED: lane={obs.lane}, "
                        f"player_lane={player.lane}, "
                        f"hit={obs.hit}, "
                        f"y={obs.y}"
                    )

                    # Se era già stato colpito non fare nulla (la collisione
                    # è già stata gestita dal check continuo sopra)
                    if obs.hit:
                        continue

                    # FIX: l'esito (evitato o no) va dedotto da obs.hit, che
                    # è impostato in modo affidabile dal check continuo
                    # durante tutta la finestra di sovrapposizione verticale
                    # con la x reale del player. Confrontare obs.lane con
                    # player.lane SOLO nell'istante di rimozione è scorretto:
                    # se il player torna nella corsia dell'ostacolo dopo
                    # averlo già schivato (ma prima che venga rimosso), le
                    # corsie risultano uguali anche se non c'è mai stata
                    # sovrapposizione reale, e il "GOOD!" non scattava più.
                    # Se siamo arrivati qui, obs.hit è False: è stato evitato.
                    metrics.log_avoidance(game_time, player.lane, obs)

                    self.feedback_text = "GOOD!"
                    self.feedback_until = time.time() + 1.0


            # ─── 1. DETERMINAZIONE DEL CUE VISIVO (FRECCIA) ───
            cue_data = None # Salviamo sia la direzione che lo stato dell'ostacolo
            
            # Filtra ostacoli non ancora superati
            valid_obstacles = [o for o in obstacles.obstacles if not o.passed]
            
            if valid_obstacles:
                # Prendi quello più vicino al giocatore (y maggiore)
                next_obstacle = max(valid_obstacles, key=lambda o: o.y)
                
                # Definiamo la direzione (se lane 0 -> RIGHT, se lane 1 -> LEFT)
                direction = "RIGHT" if next_obstacle.lane == 0 else "LEFT"
                cue_data = {"dir": direction, "visible": next_obstacle.visible}

            # ─── 2. RENDERING DELLA FRECCIA DI CUE ───
            if cue_data:
                # Logica del lampeggio:
                # Lampeggia solo se è visibile, altrimenti resta fissa
                should_draw = True
                if cue_data["visible"]:
                    # Effetto lampeggio (es: 10 volte al secondo)
                    if int(time.time() * 5) % 2 != 0:
                        should_draw = False
                
                if should_draw:
                    self.draw_cue_arrow(cue_data["dir"])

            if time.time() < self.feedback_until:
                self.draw_feedback(
                    self._screen, 
                    self._fonts, 
                    self.feedback_text, 
                    metrics.collisions, 
                    metrics.avoidances
                )

            # draw_hud(self._screen, self._fonts, remaining,
            #          player.lane, metrics.collisions, metrics.avoidances)

            self.draw_eeg_status()

            pygame.display.flip()

            if remaining <= 0:
                # Nome file fisso per raccogliere tutti i dati del software
                csv_path = metrics.export_csv(
                    self._participant,
                    "all_participants_data.csv", 
                )
                metrics.print_report()
                return ResultsScreen(self._screen, metrics, self._participant, csv_path).run()
    # ─── 3. FUNZIONE DI DISEGNO DELLA FRECCIA ───
    def draw_cue_arrow(self, direction: str) -> None:
        """Disegna una freccia geometrica o testuale al centro dello schermo."""
        center_x = ROAD_X + ROAD_W // 2
        center_y = WINDOW_H // 4 # Posizionata leggermente sopra il centro geometrico
        
        # Colore vibrante per attirare l'attenzione del soggetto (es. il tuo C_ACCENT o Verde)
        arrow_color = C_CUE 
        
        if direction == "LEFT":
            # Freccia verso SINISTRA potenziata e ingrandita
            points = [
                (center_x + 60, center_y - 25),  # Coda superiore (fusto più spesso)
                (center_x - 15, center_y - 25),  # Inizio punta sup
                (center_x - 15, center_y - 55),  # Punta esterna sup (molto più larga e visibile)
                (center_x - 75, center_y),       # Estremo punta (esteso verso sinistra)
                (center_x - 15, center_y + 55),  # Punta esterna inf
                (center_x - 15, center_y + 25),  # Inizio punta inf
                (center_x + 60, center_y + 25),  # Coda inferiore
            ]
        else:  # RIGHT
            # Freccia verso DESTRA potenziata e ingrandita
            points = [
                (center_x - 60, center_y - 25),  # Coda superiore
                (center_x + 15, center_y - 25),  # Inizio punta sup
                (center_x + 15, center_y - 55),  # Punta esterna sup
                (center_x + 75, center_y),       # Estremo punta (esteso verso destra)
                (center_x + 15, center_y + 55),  # Punta esterna inf
                (center_x + 15, center_y + 25),  # Inizio punta inf
                (center_x - 60, center_y + 25),  # Coda inferiore
            ]
            
            
        pygame.draw.polygon(self._screen, (0, 0, 0), points, 3)
        pygame.draw.polygon(self._screen, arrow_color, points)

        pygame.draw.polygon(self._screen, C_BG, points, 2)

        label = "LEFT" if direction == "LEFT" else "RIGHT"
        

        text_color = (255, 255, 255)

        outline_color = (20, 20, 20)   # nero molto scuro

        outline_size = 1               # contorno molto sottile

        text_surface = self.arrow_label_font.render(label, True, text_color)

        text_rect = text_surface.get_rect(center=(center_x, center_y))

        # Contorno

        for dx, dy in [(-outline_size, 0), (outline_size, 0),

                    (0, -outline_size), (0, outline_size)]:

            outline = self.arrow_label_font.render(label, True, outline_color)

            self._screen.blit(outline, text_rect.move(dx, dy))

        # Testo principale

        self._screen.blit(text_surface, text_rect)


    def draw_eeg_status(self) -> None:
        """Indicatore discreto che segnala che il sistema è vivo e in
        ascolto del segnale EEG. Usa un "respiro" lento (sinusoide) invece
        di un lampeggio secco, per non generare ansia nell'utente.

        Riflette lo stato reale della connessione (EEGInterface._connected):
        verde a respiro se connesso, X rossa statica se la connessione
        manca. Un piccolo chip scuro semi-trasparente sta dietro
        all'icona/testo per garantire contrasto anche su sfondi di gioco
        chiari o verdi, dove altrimenti l'indicatore verde si perderebbe.
        Non mostra nulla sulla qualità del segnale.
        """
        now = time.time()

        connected = bool(getattr(self._eeg, "_connected", False))

        dot_radius = 8
        gap        = 8
        pad_x      = 12
        pad_y      = 7
        margin     = 14

        if connected:
            # Respiro lento: ciclo di ~1.8s, mai completamente spento
            # (evita l'effetto "flash" nervoso di un blink secco 50/50).
            cycle = 1.8
            pulse = (math.sin(now * 2 * math.pi / cycle) + 1) / 2  # 0..1
            alpha = int(140 + 90 * pulse)  # range 140-230
            color = (110, 230, 160)  # verde
        else:
            alpha = 255
            color = (230, 90, 90)  # rosso

        label = "EEG"
        text_surface = self.eeg_font.render(label, True, color)
        text_w, text_h = text_surface.get_size()

        content_h = max(text_h, dot_radius * 2)
        chip_w = pad_x * 2 + text_w + gap + dot_radius * 2
        chip_h = pad_y * 2 + content_h

        chip_x = self._screen.get_width() - margin - chip_w
        chip_y = margin

        # Chip scuro semi-trasparente: garantisce leggibilità anche se
        # dietro c'è cielo/strada/erba di colore simile all'indicatore.
        chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
        pygame.draw.rect(chip_surf, (15, 20, 18, 184), chip_surf.get_rect(),
                          border_radius=chip_h // 2)

        text_y = (chip_h - text_h) // 2
        chip_surf.blit(text_surface, (pad_x, text_y))

        icon_cx = pad_x + text_w + gap + dot_radius
        icon_cy = chip_h // 2

        if connected:
            dot_surf = pygame.Surface((dot_radius * 4, dot_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*color, alpha), (dot_radius * 2, dot_radius * 2), dot_radius)
            # Sottile anello chiaro per staccare il pallino dallo sfondo scuro del chip
            pygame.draw.circle(dot_surf, (255, 255, 255, 60), (dot_radius * 2, dot_radius * 2), dot_radius, 2)
            chip_surf.blit(dot_surf, (icon_cx - dot_radius * 2, icon_cy - dot_radius * 2))
        else:
            offset = dot_radius - 1
            pygame.draw.line(chip_surf, color,
                              (icon_cx - offset, icon_cy - offset), (icon_cx + offset, icon_cy + offset), 3)
            pygame.draw.line(chip_surf, color,
                              (icon_cx - offset, icon_cy + offset), (icon_cx + offset, icon_cy - offset), 3)

        self._screen.blit(chip_surf, (chip_x, chip_y))

    def draw_feedback(self, screen, fonts, feedback_label, collisions, avoidances ) :

        pos_x = WINDOW_W // 2
        pos_y = WINDOW_H // 2
        text_surface = self.label_font.render(feedback_label, True, C_TEXT)

        # Usa la nuova costante del colore
        text_surface = self.label_font.render(feedback_label, True, C_BORDEAUX if feedback_label == "COLLISION!" else C_OK)

        text_rect = text_surface.get_rect(center=(pos_x, pos_y))

        self._screen.blit(text_surface, text_rect)