"""
lift.py — Logik für den Lift (Förderkorb).

"""

import pygame

LIFT_SPEED_BASE = 200  # Startgeschwindigkeit in Pixeln/Sekunde

# Kapazitäts-Upgrades: erhöhen wie viel Erz der Lift auf einmal trägt
# Das letzte Upgrade ("ALLES holen") leert alle Schächte gleichzeitig
LIFT_CAP_UPGRADES = [
    # (Anzeigename,     neue_Kapazität, Kosten)
    ("Kap. 20",              20,    25),
    ("Kap. 40",              40,   100),
    ("Kap. 80",              80,   400),
    ("ALLES holen",      999999,  5000),
]

# Geschwindigkeits-Upgrades: erhöhen wie schnell der Lift fährt
LIFT_SPEED_UPGRADES = [
    # (Anzeigename,  neue_Geschwindigkeit, Kosten)
    ("Speed x2",        400,   300),
    ("Speed x3",        600,  1200),
    ("Speed x4",        800,  4000),
]

MANAGER_COST = 5


class Lift:
    """
    Förderkorb der Erz aus den Schächten zur Hauptstation bringt.
    """
    def __init__(self, x, top_y, bottom_y, shaft_ys, shaft_height):
        self.x        = x
        self.top_y    = top_y     # Y-Position der Hauptstation (oben)
        self.bottom_y = bottom_y  # Y-Position des untersten Schachts
        self.shaft_ys = shaft_ys  # Y-Mittelpunkte aller Schächte
        self.shaft_h  = shaft_height

        self.y        = float(top_y)  # Aktuelle Y-Position des Lifts
        self.ore      = 0             # Erz das der Lift gerade trägt
        self.capacity = 10            # Maximales Erz das der Lift trägt
        self.speed    = LIFT_SPEED_BASE

        # Getrennte Level für Kapazität und Geschwindigkeit
        self.cap_level   = 0
        self.speed_level = 0
        self.has_manager = False

        # Aktueller Zustand der State Machine
        self.state        = "idle"
        self.target_shaft = 0    # Welcher Schacht wird angefahren?
        self.wait_timer   = 0.0  # Kurze Pause beim Sammeln/Abladen

        self.station_ore  = 0   # Erz das oben auf die Lore wartet

        self.w          = 24
        self.h          = 36
        self.font       = pygame.font.SysFont(None, 18)
        self.font_small = pygame.font.SysFont(None, 16)

    def is_full(self):
        return self.ore >= self.capacity

    def is_collect_all(self):
        """True nachdem das 'ALLES holen' Upgrade gekauft wurde."""
        return self.cap_level >= len(LIFT_CAP_UPGRADES)

    def next_cap_upgrade(self):
        """Gibt (Name, Kosten) des nächsten Kapazitäts-Upgrades zurück, oder None."""
        if self.cap_level >= len(LIFT_CAP_UPGRADES):
            return None
        u = LIFT_CAP_UPGRADES[self.cap_level]
        return u[0], u[2]

    def next_speed_upgrade(self):
        """Gibt (Name, Kosten) des nächsten Speed-Upgrades zurück, oder None."""
        if self.speed_level >= len(LIFT_SPEED_UPGRADES):
            return None
        u = LIFT_SPEED_UPGRADES[self.speed_level]
        return u[0], u[2]

    def do_cap_upgrade(self):
        if self.cap_level < len(LIFT_CAP_UPGRADES):
            self.capacity  = LIFT_CAP_UPGRADES[self.cap_level][1]
            self.cap_level += 1

    def do_speed_upgrade(self):
        if self.speed_level < len(LIFT_SPEED_UPGRADES):
            self.speed        = LIFT_SPEED_UPGRADES[self.speed_level][1]
            self.speed_level += 1

    def hire_manager(self):
        self.has_manager = True

    def click(self):
        """Manuell starten (wenn idle)."""
        if self.state == "idle":
            self.state        = "going_down"
            self.target_shaft = 0

    def update(self, dt, shafts):

        if self.state == "idle":
            # Manager startet automatisch, ABER nur wenn irgendwo Erz wartet
            if self.has_manager:
                i = 0
                for s in shafts:
                    if s.unlocked and s.ore_stored > 0:
                        self.target_shaft = i
                        self.state        = "going_down"
                        break
                    i += 1

        elif self.state == "going_down":
            target_y  = float(self.shaft_ys[self.target_shaft])
            self.y    = min(self.y + self.speed * dt, target_y)
            if self.y >= target_y:
                self.state      = "collecting"
                self.wait_timer = 0.25

        elif self.state == "collecting":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                if self.is_collect_all():
                    # Letztes Upgrade: alle Schächte auf einmal leeren
                    for s in shafts:
                        if s.unlocked:
                            take = min(s.ore_stored, self.capacity - self.ore)
                            s.ore_stored -= take
                            self.ore     += take
                else:
                    shaft = shafts[self.target_shaft]
                    take  = min(shaft.ore_stored, self.capacity - self.ore)
                    shaft.ore_stored -= take
                    self.ore         += take

                # Nächsten Schacht anfahren oder hochfahren
                next_shaft = self._find_next_shaft(shafts)
                if next_shaft is not None and not self.is_full():
                    self.target_shaft = next_shaft
                    self.state        = "going_down"
                elif self.ore > 0:
                    self.state = "going_up"   # Nur hochfahren wenn Erz vorhanden
                else:
                    self.state = "idle"       # Kein Erz gesammelt → direkt idle

        elif self.state == "going_up":
            self.y = max(self.y - self.speed * dt, float(self.top_y))
            if self.y <= self.top_y:
                self.state      = "depositing"
                self.wait_timer = 0.25

        elif self.state == "depositing":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.station_ore += self.ore  # Erz in Hauptstation ablegen
                self.ore          = 0
                self.state        = "idle"

    def _find_next_shaft(self, shafts):
        """Sucht den nächsten Schacht mit Erz (nach dem aktuellen)."""
        for i in range(self.target_shaft + 1, len(shafts)):
            if shafts[i].unlocked and shafts[i].ore_stored > 0:
                return i
        return None

    def draw(self, surface, station_x, station_y, station_w, station_h, avg_ore_value=1.0):
        import visuals
        visuals.draw_lift_station(surface, station_x, station_y, station_w, station_h,
                                  self.station_ore, avg_ore_value, self.font_small)
        visuals.draw_lift(surface, self)
