import pygame

CART_SPEED_BASE = 80        # Pixel pro Sekunde
CART_CAPACITY_UPGRADES = [20, 40, 80]       # Kapazität nach Upgrade
CART_SPEED_UPGRADES    = [120, 180, 260]    # Geschwindigkeit nach Upgrade
CART_UPGRADE_COSTS     = [400, 1500, 5000]  # Kosten pro Upgrade

class Cart:
    def __init__(self, lift_x, station_x, y):
        """
        lift_x    : X wo der Lift ist (Abholstation)
        station_x : X der Münzstation (rechts)
        y         : Feste Y-Linie auf der die Lore fährt
        """
        self.lift_x     = lift_x
        self.station_x  = station_x
        self.y          = y
        self.x          = float(station_x)  # Startet an der Station

        self.ore        = 0
        self.capacity   = 10
        self.speed      = CART_SPEED_BASE

        self.upgrade_level = 0

        # Zustand: "idle", "going_to_lift", "loading", "going_to_station", "unloading"
        self.state      = "idle"
        self.wait_timer = 0.0

        self.w = 28
        self.h = 18
        self.font = pygame.font.SysFont(None, 18)

    # ------------------------------------------------------------------ #
    #  Infos
    # ------------------------------------------------------------------ #
    def next_upgrade_cost(self):
        if self.upgrade_level >= len(CART_UPGRADE_COSTS):
            return None
        return CART_UPGRADE_COSTS[self.upgrade_level]

    # ------------------------------------------------------------------ #
    #  Aktionen
    # ------------------------------------------------------------------ #
    def upgrade(self):
        if self.upgrade_level < len(CART_UPGRADE_COSTS):
            self.capacity = CART_CAPACITY_UPGRADES[self.upgrade_level]
            self.speed    = CART_SPEED_UPGRADES[self.upgrade_level]
            self.upgrade_level += 1

    def notify_ore_available(self, amount):
        """Wird aufgerufen wenn der Lift oben angekommen ist und entladen hat."""
        self._pending_ore = getattr(self, '_pending_ore', 0) + amount
        if self.state == "idle" and self._pending_ore > 0:
            self.state = "going_to_lift"

    # ------------------------------------------------------------------ #
    #  Update – gibt Münzwert zurück wenn an Station angekommen
    # ------------------------------------------------------------------ #
    def update(self, dt, shafts):
        coins = 0
        pending = getattr(self, '_pending_ore', 0)

        if self.state == "idle":
            if pending > 0:
                self.state = "going_to_lift"

        elif self.state == "going_to_lift":
            target = float(self.lift_x)
            if self.x > target:
                self.x = max(self.x - self.speed * dt, target)
            else:
                self.x = target
                self.state = "loading"
                self.wait_timer = 0.3

        elif self.state == "loading":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                take = min(pending, self.capacity)
                self.ore += take
                self._pending_ore = pending - take
                self.state = "going_to_station"

        elif self.state == "going_to_station":
            target = float(self.station_x)
            if self.x < target:
                self.x = min(self.x + self.speed * dt, target)
            else:
                self.x = target
                self.state = "unloading"
                self.wait_timer = 0.3

        elif self.state == "unloading":
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                coins = self.ore     # Erz → Münzen (Wert wird in game.py berechnet)
                self.ore = 0
                # Noch mehr pending?
                if getattr(self, '_pending_ore', 0) > 0:
                    self.state = "going_to_lift"
                else:
                    self.state = "idle"

        return coins

    # ------------------------------------------------------------------ #
    #  Draw
    # ------------------------------------------------------------------ #
    def draw(self, surface, line_y):
        # Fahrlinie
        pygame.draw.line(surface, (220, 220, 220),
                         (self.lift_x - 10, line_y),
                         (self.station_x + self.w + 10, line_y), 2)

        # Münzstation (festes graues Rechteck rechts)
        station_rect = pygame.Rect(self.station_x, line_y - 20, 40, 28)
        pygame.draw.rect(surface, (180, 150, 50), station_rect)
        pygame.draw.rect(surface, (255, 220, 80), station_rect, 1)
        st_surf = self.font.render("$", True, (255, 240, 100))
        surface.blit(st_surf, (self.station_x + 14, line_y - 14))

        # Lore
        if self.state in ("going_to_lift", "going_to_station"):
            color = (100, 200, 120)
        elif self.ore > 0:
            color = (60, 160, 80)
        else:
            color = (80, 120, 90)

        rect = pygame.Rect(int(self.x) - self.w // 2, line_y - self.h // 2, self.w, self.h)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (180, 255, 180), rect, 1)

        # Erz-Anzeige
        ore_surf = self.font.render(f"{self.ore}/{self.capacity}", True, (255, 255, 255))
        surface.blit(ore_surf, (int(self.x) - self.w // 2, line_y - self.h // 2 - 13))
