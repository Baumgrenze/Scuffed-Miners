"""
cart.py — Logik für die Erz-Lore (Minenwagen).
"""

import pygame

# Zwei unabhängige Upgrade-Pfade
CART_CAP_UPGRADES = [
    # (Anzeigename,     neue_Kapazität, Kosten)
    ("Kap. 20",              20,    20),
    ("Kap. 40",              40,    80),
    ("Kap. 80",              80,   300),
    ("ALLES holen",      999999,  3500),
]

CART_SPEED_UPGRADES = [
    # (Anzeigename,  neue_Geschwindigkeit, Kosten)
    ("Speed x2",        400,   250),
    ("Speed x3",        600,  1000),
    ("Speed x4",        800,  3000),
]


class Cart:
    """
    Die Lore transportiert Erz von der Hauptstation zur Münzstation.
    """
    def __init__(self, lift_x, station_x, line_y):
        self.lift_x    = lift_x      # X der Hauptstation (Abholpunkt)
        self.station_x = station_x  # X der Münzstation (Ablieferungspunkt)
        self.line_y    = line_y

        self.x         = float(station_x)  # Startet an der Münzstation
        self.ore       = 0
        self.capacity  = 10
        self.speed     = 200

        self.cap_level   = 0
        self.speed_level = 0
        self.state       = "idle"
        self.wait_timer  = 0.0
        self._pending_ore = 0   # Erz das in der Hauptstation wartet

        self.w    = 28
        self.h    = 18
        self.font = pygame.font.SysFont(None, 18)

    def is_collect_all(self):
        """True nachdem das 'ALLES holen' Upgrade gekauft wurde."""
        return self.cap_level >= len(CART_CAP_UPGRADES)

    def next_cap_upgrade(self):
        if self.cap_level >= len(CART_CAP_UPGRADES):
            return None
        u = CART_CAP_UPGRADES[self.cap_level]
        return u[0], u[2] #gibt das nächste upgrade zurück

    def next_speed_upgrade(self):
        if self.speed_level >= len(CART_SPEED_UPGRADES):
            return None
        u = CART_SPEED_UPGRADES[self.speed_level]
        return u[0], u[2]

    def do_cap_upgrade(self):
        if self.cap_level < len(CART_CAP_UPGRADES):  #checkt ob upgegradet wurde, holt das upgrade und merkt es sich
            self.capacity  = CART_CAP_UPGRADES[self.cap_level][1]
            self.cap_level += 1

    def do_speed_upgrade(self):
        if self.speed_level < len(CART_SPEED_UPGRADES):
            self.speed        = CART_SPEED_UPGRADES[self.speed_level][1]
            self.speed_level += 1

    def notify_ore(self, amount):
        """Wird aufgerufen wenn der Lift Erz in der Station abliefert."""
        self._pending_ore += amount
        if self.state == "idle":
            self.state = "going_to_lift"

    def update(self, dt):
        """
        Gibt (ore_loaded, ore_delivered) zurück:
        ore_loaded    = Erz das die Lore gerade geladen hat (Anzeige sofort aktualisieren)
        ore_delivered = Erz das an der Münzstation angekommen ist (Münzen gutschreiben)
        """
        ore_loaded = ore_delivered = 0

        if self.state == "idle":
            if self._pending_ore > 0:
                self.state = "going_to_lift"

        elif self.state == "going_to_lift":
            self.x = max(self.x - self.speed * dt, float(self.lift_x))
            if self.x <= self.lift_x:
                self.state, self.wait_timer = "loading", 0.2

        elif self.state == "loading":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                take               = self._pending_ore if self.is_collect_all() \
                                     else min(self._pending_ore, self.capacity)
                self.ore          += take
                self._pending_ore -= take
                ore_loaded         = take
                self.state         = "going_to_station"     #nimmt alles bis zur cap mit und geht dann zur station

        elif self.state == "going_to_station":
            self.x = min(self.x + self.speed * dt, float(self.station_x))
            if self.x >= self.station_x:
                self.state, self.wait_timer = "unloading", 0.2

        elif self.state == "unloading":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                ore_delivered = self.ore
                self.ore      = 0
                self.state    = "going_to_lift" if self._pending_ore > 0 else "idle"

        return ore_loaded, ore_delivered

    def draw(self, surface, avg_ore_value):
        import visuals
        visuals.draw_cart_scene(surface, self, avg_ore_value, self.font)
