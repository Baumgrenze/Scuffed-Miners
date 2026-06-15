"""
visuals.py — Alle Zeichen-Funktionen für Scuffed Miners.

Hier steht nur wie Dinge aussehen — keine Spiellogik. Ein haufen von sich wiederholenden
Commands die die visuals machen
"""

import pygame
import random


# =======================================================================
#  FARB-PALETTE
# =======================================================================
C_DIRT_DARK   = (55,  40,  25)
C_DIRT_MID    = (80,  58,  35)
C_DIRT_LIGHT  = (110, 82,  50)
C_ROCK        = (70,  70,  75)
C_ROCK_LIGHT  = (110, 110, 118)
C_WOOD        = (120, 85,  45)
C_WOOD_DARK   = (80,  55,  28)
C_STEEL       = (90,  100, 115)
C_STEEL_LIGHT = (140, 155, 175)
C_GOLD        = (255, 210,  50)
C_GOLD_DARK   = (180, 140,  20)
C_ORE         = (60,  180, 220)
C_ORE_DARK    = (30,  110, 150)
C_SHAFT_BG    = (38,  28,  18)
C_SKY         = (28,  32,  48)
C_GRASS       = (40,  90,  40)
C_GRASS_DARK  = (28,  65,  28)
C_PANEL       = (22,  22,  36)
C_PANEL_BORD  = (55,  55,  80)
C_TEXT        = (220, 220, 220)
C_GREEN_OK    = (60,  230,  80)
C_RED_ERR     = (220,  70,  70)
C_LIFT_BODY   = (70,  130, 200)
C_LIFT_MOVE   = (100, 200, 255)
C_LIFT_FULL   = (255, 100,  70)
C_CART_BODY   = (60,  155,  75)
C_CART_MOVE   = (100, 215, 120)
C_MANAGER     = (40,  100, 200)


# =======================================================================
#  EXPLOSION
# =======================================================================
class Explosion:
    """Partikelexplosion beim Freischalten eines Schachts."""

    DURATION = 0.7  # Sekunden bis die Animation fertig ist

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 0.0

        # Jedes Partikel hat eine Richtung, Geschwindigkeit und Farbe
        self.particles = []
        for _ in range(28):
            dx    = random.uniform(-1, 1)
            dy    = random.uniform(-1, 1)
            speed = random.uniform(40, 140)
            color = random.choice([
                (255, 200,  50),
                (255, 120,  30),
                (200,  80,  20),
                (255, 255, 100),
                (180, 100,  20),
            ])
            self.particles.append((dx, dy, speed, color))

    @property
    def done(self):
        return self.timer >= self.DURATION

    def update(self, dt):
        self.timer += dt

    def draw(self, surface):
        if self.done:
            return

        # t geht von 0.0 (Anfang) bis 1.0 (Ende)
        t = self.timer / self.DURATION

        for dx, dy, speed, color in self.particles:
            px   = int(self.x + dx * speed * t)
            py   = int(self.y + dy * speed * t)
            size = max(1, int(6 * (1 - t)))   # Partikel werden kleiner

            # Farbe ausblenden
            r = int(color[0] * (1 - t * 0.8))
            g = int(color[1] * (1 - t * 0.8))
            b = int(color[2] * (1 - t * 0.8))

            pygame.draw.circle(surface, (r, g, b), (px, py), size)


# =======================================================================
#  HINTERGRUND
# =======================================================================
def draw_background(surf, screen_w, screen_h, shaft_start_y):
    """Himmel oben, Erde unten mit Stein-Schichten."""

    # Himmel
    pygame.draw.rect(surf, C_SKY, (0, 0, screen_w, shaft_start_y))

    # Gras-Streifen
    pygame.draw.rect(surf, C_GRASS,      (0, shaft_start_y - 12, screen_w, 8))
    pygame.draw.rect(surf, C_GRASS_DARK, (0, shaft_start_y - 5,  screen_w, 5))

    # Erde
    pygame.draw.rect(surf, C_DIRT_DARK, (0, shaft_start_y, screen_w, screen_h - shaft_start_y))

    # Waagrechte Stein-Linien
    for i in range(3):
        y = shaft_start_y + 80 + i * 160
        if y < screen_h:
            pygame.draw.line(surf, C_ROCK, (0, y), (screen_w, y), 1)

    # Steinflecken (feste Positionen für reproduzierbares Aussehen)
    stones = [
        (130, 230, 18, 10),
        (300, 310, 22, 12),
        (500, 260, 14,  8),
        (650, 380, 20, 11),
        (820, 290, 16,  9),
        (200, 450, 24, 13),
        (420, 510, 18, 10),
        (700, 480, 20, 11),
    ]
    for sx, sy, sw, sh in stones:
        if sy < screen_h:
            pygame.draw.rect(surf, C_ROCK, (sx, sy, sw, sh), border_radius=3)


# =======================================================================
#  MINENSCHACHT
# =======================================================================
def draw_shaft(surf, shaft, font_med, font_small):
    """
    Zeichnet einen Minenschacht.
    Gesperrte Schächte sehen aus wie normaler Erdboden.
    """
    x = shaft.x
    y = shaft.y
    w = shaft.w
    h = shaft.h

    # --- Gesperrter Schacht: sieht aus wie Erde ---
    if not shaft.unlocked:
        pygame.draw.rect(surf, C_DIRT_DARK, (x, y, w, h))
        pygame.draw.rect(surf, C_DIRT_MID,  (x + 40,  y + 25, 90, 12), border_radius=3)
        pygame.draw.rect(surf, C_ROCK,      (x + 200, y + 55, 60,  8), border_radius=2)
        pygame.draw.rect(surf, C_DIRT_MID,  (x + 380, y + 30, 70, 10), border_radius=3)
        return

    # --- Entsperrter Schacht ---

    # Hintergrund (etwas dunkler wenn Manager aktiv)
    if shaft.has_manager:
        bg_color = (30, 22, 14)
    else:
        bg_color = C_SHAFT_BG
    pygame.draw.rect(surf, bg_color, (x, y, w, h))

    # Holzstützen alle 120px
    for sx in range(x + 30, x + w - 10, 120):
        # Linke Stütze
        pygame.draw.rect(surf, C_WOOD_DARK, (sx,     y + 2, 6, h - 4))
        pygame.draw.rect(surf, C_WOOD,      (sx + 1, y + 2, 3, h - 4))
        # Rechte Stütze
        pygame.draw.rect(surf, C_WOOD_DARK, (sx + 30, y + 2, 6, h - 4))
        pygame.draw.rect(surf, C_WOOD,      (sx + 31, y + 2, 3, h - 4))
        # Oberer Balken
        pygame.draw.rect(surf, C_WOOD_DARK, (sx, y + 2,     36, 6))
        pygame.draw.rect(surf, C_WOOD,      (sx + 1, y + 3, 34, 3))
        # Unterer Balken
        pygame.draw.rect(surf, C_WOOD_DARK, (sx, y + h - 8, 36, 6))
        pygame.draw.rect(surf, C_WOOD,      (sx + 1, y + h - 7, 34, 3))

    # Rahmen
    pygame.draw.rect(surf, C_WOOD_DARK, (x, y, w, h), 2)

    # Titel
    title = f"Schacht {shaft.shaft_id + 1}   +{shaft.ore_value} Muenzen/Erz"
    surf.blit(font_med.render(title, True, C_GOLD), (x + 8, y + 4))

    # Manager-Status (rechts oben)
    if shaft.has_manager:
        mgr_text  = "Manager"
        mgr_color = C_GREEN_OK
    else:
        mgr_text  = "kein Manager"
        mgr_color = C_RED_ERR
    surf.blit(font_small.render(mgr_text, True, mgr_color), (x + w - 80, y + 5))

    # Miner zeichnen
    miner_x = x + 8
    miner_y = y + 22
    for i, miner in enumerate(shaft.miners):
        draw_miner(surf, miner_x + i * 30, miner_y, miner, shaft.mine_progress)

    # Manager-Figur am rechten Rand
    if shaft.has_manager:
        draw_manager(surf, x + w - 38, miner_y - 2)

    # Erzlager-Info unten
    info_y = y + h - 18
    surf.blit(font_small.render(f"Lager: {shaft.ore_stored}", True, C_ORE),        (x + 8,   info_y))
    surf.blit(font_small.render(f"Miner: {len(shaft.miners)}/10", True, C_TEXT), (x + 110, info_y))

    # Kleine Ore-Symbole
    for k in range(min(shaft.ore_stored, 8)):
        ox = x + 220 + k * 14
        pygame.draw.rect(surf, C_ORE_DARK, (ox,     info_y + 3, 10, 8), border_radius=2)
        pygame.draw.rect(surf, C_ORE,      (ox + 1, info_y + 4,  7, 5), border_radius=1)


def draw_miner(surf, x, y, miner, mine_progress=0.0):
    """
    Zeichnet einen Miner als kleines Rechteck mit Helm.

    Farben:
      Orange = schürft gerade (active)
      Gelb   = fertig, wartet auf Klick (ready)
      Dunkel = noch nicht gestartet
    """
    # Körper-Farbe je nach Zustand
    if miner.active:
        body_col = (200, 140, 30)
        helm_col = (80,  60,  20)
        lamp_col = (100, 100, 40)
    elif miner.ready:
        body_col = (255, 220, 50)
        helm_col = (120, 90,  30)
        lamp_col = (255, 255, 100)
    else:
        body_col = (100, 80,  30)
        helm_col = (60,  45,  15)
        lamp_col = (80,  80,  40)

    # Körper
    pygame.draw.rect(surf, body_col, (x,     y,     22, 22))
    pygame.draw.rect(surf, (0, 0, 0), (x,    y,     22, 22), 1)

    # Helm
    pygame.draw.rect(surf, helm_col, (x + 1, y + 1, 20, 7))

    # Helmlampe
    pygame.draw.rect(surf, lamp_col, (x + 8, y + 2, 6, 4), border_radius=1)

    # Fortschrittsbalken (nur wenn aktiv)
    if miner.active:
        pygame.draw.rect(surf, (50, 50, 50), (x, y + 23, 22, 5))
        fill = int(22 * mine_progress)
        if fill > 0:
            pygame.draw.rect(surf, (80, 220, 100), (x, y + 23, fill, 5))

    # Grüner Rahmen wenn bereit
    if miner.ready:
        pygame.draw.rect(surf, (80, 255, 80), (x, y, 22, 22), 2)


def draw_manager(surf, x, y):
    """
    Zeichnet den Manager: blauer Körper, weißer Helm, Klemmbrett.
    Größer als ein normaler Miner.
    """
    # Körper
    pygame.draw.rect(surf, C_MANAGER, (x,     y,     22, 26))
    pygame.draw.rect(surf, (0, 0, 0), (x,     y,     22, 26), 1)

    # Helm (weiß = Chef-Helm)
    pygame.draw.rect(surf, (210, 210, 210), (x + 1, y + 1, 20, 7))
    pygame.draw.rect(surf, (160, 160, 160), (x + 1, y + 6, 20, 2))

    # Klemmbrett
    pygame.draw.rect(surf, (240, 220, 160), (x + 6, y + 10, 10, 13), border_radius=1)
    pygame.draw.rect(surf, (100, 80,   30), (x + 6, y + 10, 10, 13), 1, border_radius=1)

    # Linien auf dem Klemmbrett
    for line_y in range(y + 12, y + 21, 3):
        pygame.draw.line(surf, (120, 90, 30), (x + 8, line_y), (x + 14, line_y), 1)

    # "M" auf dem Helm
    label_font = pygame.font.SysFont(None, 11)
    surf.blit(label_font.render("M", True, C_MANAGER), (x + 7, y + 1))


# =======================================================================
#  LIFT + HAUPTSTATION
# =======================================================================
def draw_lift_station(surf, station_x, station_y, station_w, station_h,
                      station_ore, avg_ore_value, font):
    """Zeichnet die Hauptstation mit Förderturm-Silhouette und Erz-Anzeige."""
    sx = station_x
    sy = station_y
    sw = station_w
    sh = station_h

    # Grundkörper
    pygame.draw.rect(surf, C_STEEL,       (sx, sy, sw, sh))
    pygame.draw.rect(surf, C_STEEL_LIGHT, (sx, sy, sw, sh), 2)

    # Dreieck-Dach
    roof = [(sx, sy), (sx + sw, sy), (sx + sw // 2, sy - 18)]
    pygame.draw.polygon(surf, C_STEEL,       roof)
    pygame.draw.polygon(surf, C_STEEL_LIGHT, roof, 2)

    # Förderrad oben
    wx = sx + sw // 2
    wy = sy - 18
    pygame.draw.circle(surf, C_WOOD_DARK, (wx, wy), 10)
    pygame.draw.circle(surf, C_WOOD,      (wx, wy),  8)
    pygame.draw.circle(surf, C_STEEL,     (wx, wy),  3)
    pygame.draw.line(surf, C_WOOD_DARK, (wx - 3, wy + 10), (wx - 3, sy + sh), 2)

    # Fenster
    pygame.draw.rect(surf, C_SHAFT_BG,  (sx + 8, sy + 6, sw - 16, sh - 12), border_radius=2)
    pygame.draw.rect(surf, C_GOLD_DARK, (sx + 8, sy + 6, sw - 16, sh - 12), 1, border_radius=2)

    # Beschriftung
    surf.blit(font.render("STATION", True, C_GOLD),            (sx + 4, sy + 3))
    surf.blit(font.render(f"Erz: {station_ore}", True, C_ORE), (sx + 4, sy + sh - 14))

    val = int(station_ore * avg_ore_value)
    surf.blit(font.render(f"= {val} Mz", True, C_GOLD), (sx, sy + sh + 3))


def draw_lift(surf, lift):
    """Zeichnet die Lift-Kabine und die Schienen."""
    rail_x = lift.x + lift.w // 2

    # Schienen
    pygame.draw.line(surf, C_STEEL, (rail_x - 4, lift.top_y), (rail_x - 4, lift.bottom_y), 2)
    pygame.draw.line(surf, C_STEEL, (rail_x + 4, lift.top_y), (rail_x + 4, lift.bottom_y), 2)

    # Querstreben
    for ry in range(lift.top_y, lift.bottom_y, 20):
        pygame.draw.line(surf, C_STEEL, (rail_x - 4, ry), (rail_x + 4, ry), 1)

    # Kabinen-Farbe je nach Zustand
    lx = int(lift.x)
    ly = int(lift.y) - lift.h // 2

    if lift.state in ("going_up", "going_down"):
        body_color = C_LIFT_MOVE
    elif lift.is_full():
        body_color = C_LIFT_FULL
    else:
        body_color = C_LIFT_BODY

    # Kabine
    pygame.draw.rect(surf, body_color,    (lx, ly, lift.w, lift.h))
    pygame.draw.rect(surf, C_STEEL_LIGHT, (lx, ly, lift.w, lift.h), 2)

    # Dach-Streifen
    pygame.draw.rect(surf, C_STEEL_LIGHT, (lx + 1, ly + 1, lift.w - 2, 4))

    # Seile
    pygame.draw.line(surf, C_WOOD_DARK, (lx + 4,            ly), (rail_x - 4, lift.top_y), 1)
    pygame.draw.line(surf, C_WOOD_DARK, (lx + lift.w - 4,   ly), (rail_x + 4, lift.top_y), 1)

    # Erz-Anzeige über der Kabine
    label_font = lift.font_small
    surf.blit(label_font.render(f"{lift.ore}/{lift.capacity}", True, (255, 255, 255)),
              (lx - 2, ly - 13))


# =======================================================================
#  LORE + SCHIENE + MÜNZSTATION
# =======================================================================
def draw_cart_scene(surf, cart, avg_ore_value, font_small):
    """Zeichnet Schienen, Münzstation und die Lore (Minenwagen)."""
    lx = cart.lift_x
    sx = cart.station_x
    ly = cart.line_y

    # Schienen
    pygame.draw.line(surf, C_STEEL, (lx - 8, ly - 3), (sx + 48, ly - 3), 3)
    pygame.draw.line(surf, C_STEEL, (lx - 8, ly + 3), (sx + 48, ly + 3), 3)

    # Schwellen
    for tx in range(lx - 8, sx + 48, 14):
        pygame.draw.rect(surf, C_WOOD_DARK, (tx, ly - 4, 8, 8))

    # Münzstation
    pygame.draw.rect(surf, (100, 80, 20), (sx,      ly - 28, 48, 36))
    pygame.draw.rect(surf, C_GOLD,        (sx,      ly - 28, 48, 36), 2)
    pygame.draw.polygon(surf, C_GOLD_DARK, [(sx, ly - 28), (sx + 48, ly - 28), (sx + 24, ly - 44)])
    pygame.draw.polygon(surf, C_GOLD,      [(sx, ly - 28), (sx + 48, ly - 28), (sx + 24, ly - 44)], 2)

    dollar_font = pygame.font.SysFont(None, 28)
    surf.blit(dollar_font.render("$", True, C_GOLD), (sx + 16, ly - 20))

    # Lore (Minenwagen)
    cx = int(cart.x)
    cw = cart.w
    ch = cart.h

    if cart.state in ("going_to_lift", "going_to_station"):
        body_color = C_CART_MOVE
    elif cart.ore > 0:
        body_color = C_CART_BODY
    else:
        body_color = (55, 110, 65)

    # Trapez-Form für die Lore
    body_pts = [
        (cx - cw // 2 - 3, ly - ch // 2),
        (cx + cw // 2 + 3, ly - ch // 2),
        (cx + cw // 2,     ly + ch // 2),
        (cx - cw // 2,     ly + ch // 2),
    ]
    pygame.draw.polygon(surf, body_color,    body_pts)
    pygame.draw.polygon(surf, C_STEEL_LIGHT, body_pts, 2)

    # Erz in der Lore anzeigen
    if cart.ore > 0:
        pygame.draw.rect(surf, C_ORE_DARK, (cx - cw // 2 + 2, ly - ch // 2 + 2, cw - 2, ch // 2 - 2), border_radius=2)
        pygame.draw.rect(surf, C_ORE,      (cx - cw // 2 + 4, ly - ch // 2 + 4, cw - 6, ch // 2 - 5), border_radius=1)

    # Räder
    for wx in [cx - cw // 2 + 4, cx + cw // 2 - 4]:
        pygame.draw.circle(surf, C_STEEL,       (wx, ly + ch // 2), 5)
        pygame.draw.circle(surf, C_STEEL_LIGHT, (wx, ly + ch // 2), 3)

    # Erz-Anzeige über der Lore
    surf.blit(font_small.render(f"{cart.ore}/{cart.capacity}", True, C_TEXT),
              (cx - cw // 2, ly - ch // 2 - 13))


# =======================================================================
#  HUD (Kopfleiste)
# =======================================================================
def draw_hud(surf, screen_w, coins, message, message_timer,
             font_large, font_medium, font_small):
    """Kopfleiste mit Münzanzeige und Feedback-Nachricht."""

    # Hintergrund der Leiste
    pygame.draw.rect(surf, (14, 14, 24), (0, 0, screen_w, 60))
    pygame.draw.rect(surf, C_GOLD_DARK,  (0, 0, screen_w, 60), 1)

    # Kleines Dreieck als Münz-Icon
    pygame.draw.polygon(surf, C_GOLD,      [(10, 29), (22, 17), (22, 41)])
    pygame.draw.polygon(surf, C_GOLD_DARK, [(11, 29), (21, 18), (21, 40)])

    # Titel und Tastenkürzel
    surf.blit(font_large.render("Scuffed Miners", True, C_GOLD),       (30,  8))
    surf.blit(font_small.render("F11 = Vollbild",  True, (80, 80, 100)), (30, 44))

    # Münzanzeige rechts
    coin_surf = font_large.render(f"{int(coins):,}", True, C_GOLD)
    surf.blit(coin_surf, (screen_w - coin_surf.get_width() - 65, 12))
    surf.blit(font_medium.render("Muenzen", True, C_GOLD_DARK), (screen_w - 63, 34))

    # Feedback-Nachricht (blendet über die Zeit aus)
    if message_timer > 0:
        alpha    = min(255, int(message_timer * 120))
        msg_surf = font_medium.render(message, True, (90, 255, 140))
        msg_surf.set_alpha(alpha)
        surf.blit(msg_surf, (200, 20))


# =======================================================================
#  PANEL-HINTERGRUND
# =======================================================================
def draw_panel(surf, x, y, w, h):
    """Dunkles Hintergrund-Panel für Button-Bereiche."""
    pygame.draw.rect(surf, C_PANEL,      (x - 3, y, w + 6, h))
    pygame.draw.rect(surf, C_PANEL_BORD, (x - 3, y, w + 6, h), 1)
    pygame.draw.line(surf, (70, 70, 95), (x - 3, y), (x + w + 3, y), 1)


# =======================================================================
#  WIN-SCREEN
# =======================================================================
def draw_win_screen(surf, screen_w, screen_h, coins,
                    font_win, font_win2, font_medium):
    """Overlay wenn der Spieler gewonnen hat."""

    # Halbtransparentes Schwarz über alles legen
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surf.blit(overlay, (0, 0))

    # Box in der Mitte
    cx = screen_w // 2
    cy = screen_h // 2
    bw = 580
    bh = 280

    # Mehrfacher Rahmen für Glüh-Effekt
    pygame.draw.rect(surf, C_GOLD_DARK,      (cx - bw // 2 - 6, cy - bh // 2 - 6, bw + 12, bh + 12), 6, border_radius=8)
    pygame.draw.rect(surf, C_GOLD,           (cx - bw // 2 - 3, cy - bh // 2 - 3, bw + 6,  bh + 6),  3, border_radius=8)
    pygame.draw.rect(surf, (255, 240, 180),  (cx - bw // 2 - 1, cy - bh // 2 - 1, bw + 2,  bh + 2),  1, border_radius=8)

    # Box-Hintergrund
    pygame.draw.rect(surf, (30, 25, 8), (cx - bw // 2, cy - bh // 2, bw, bh), border_radius=6)

    # Pokal-Symbol
    tx = cx
    ty = cy - 80
    trophy_pts = [
        (tx - 18, ty + 20), (tx - 25, ty + 35), (tx + 25, ty + 35), (tx + 18, ty + 20),
        (tx + 18, ty),      (tx + 25, ty - 10),  (tx + 10, ty - 25), (tx - 10, ty - 25),
        (tx - 25, ty - 10), (tx - 18, ty),
    ]
    pygame.draw.polygon(surf, C_GOLD_DARK, trophy_pts)
    pygame.draw.polygon(surf, C_GOLD,      trophy_pts, 2)

    # Texte
    texts = [
        ("GEWONNEN!",                    C_GOLD,        -20, font_win),
        ("Mine vollstaendig ausgebaut!", C_TEXT,         40, font_win2),
        (f"Endkapital: {int(coins):,} Muenzen", C_GOLD, 85, font_win2),
        ("Fenster schliessen zum Beenden", (140, 140, 140), 125, font_medium),
    ]
    for text, color, y_off, font in texts:
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(cx, cy + y_off))
        surf.blit(text_surf, text_rect)