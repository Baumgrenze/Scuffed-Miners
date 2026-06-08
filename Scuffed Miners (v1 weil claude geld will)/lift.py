import pygame

LIFT_SPEED          = 120       # Pixel pro Sekunde
LIFT_BASE_CAPACITY  = 10        # Startwert
LIFT_CAPACITY_UPGRADES = [20, 40, 80, 999999]   # Kapazität nach jedem Upgrade
LIFT_UPGRADE_COSTS     = [300, 900, 3000, 10000] # Kosten pro Upgrade (letztes = alle Schächte)
MANAGER_COST           = 500

class Lift:
    def __init__(self, x, top_y, bottom_y, shaft_ys, shaft_height):
        """
        x        : X-Position des Lifts
        top_y    : Y-Position oben (Abgabe)
        bottom_y : Y-Position des untersten Schachts
        shaft_ys : Liste der Y-Positionen der Schächte (zum Stoppen)
        """
        self.x          = x
        self.top_y      = top_y
        self.bottom_y   = bottom_y
        self.shaft_ys   = shaft_ys      # Y-Mitte jedes Schachts
        self.shaft_h    = shaft_height

        self.y          = float(top_y)  # Aktuelle Y-Position
        self.ore        = 0             # Aktuell geladenes Erz
        self.capacity   = LIFT_BASE_CAPACITY

        self.upgrade_level  = 0
        self.has_manager    = False

        # Zustand: "idle", "going_down", "collecting", "going_up", "unloading"
        self.state          = "idle"
        self.target_shaft   = 0        # Welchen Schacht als nächstes anfahren
        self.collect_timer  = 0.0      # Kurze Pause beim Sammeln

        self.w = 24
        self.h = 36

        self.font = pygame.font.SysFont(None, 18)

    # ------------------------------------------------------------------ #
    #  Infos
    # ------------------------------------------------------------------ #
    def is_full(self):
        return self.ore >= self.capacity

    def next_upgrade_cost(self):
        if self.upgrade_level >= len(LIFT_UPGRADE_COSTS):
            return None
        return LIFT_UPGRADE_COSTS[self.upgrade_level]

    def is_last_upgrade(self):
        """Letztes Upgrade = holt alle Schächte gleichzeitig."""
        return self.upgrade_level == len(LIFT_UPGRADE_COSTS) - 1

    # ------------------------------------------------------------------ #
    #  Aktionen
    # ------------------------------------------------------------------ #
    def upgrade(self):
        if self.upgrade_level < len(LIFT_CAPACITY_UPGRADES):
            self.capacity = LIFT_CAPACITY_UPGRADES[self.upgrade_level]
            self.upgrade_level += 1

    def hire_manager(self):
        self.has_manager = True

    def click(self):
        """Spieler klickt manuell auf den Lift."""
        if self.state == "idle":
            self.state = "going_down"
            self.target_shaft = 0

    # ------------------------------------------------------------------ #
    #  Update
    # ------------------------------------------------------------------ #
    def update(self, dt, shafts):
        """
        shafts: Liste aller MineShaft-Objekte
        Gibt gesammeltes Erz (als Münzwert) zurück wenn oben angekommen.
        """
        coins_earned = 0

        if self.state == "idle":
            if self.has_manager and not self.is_full():
                # Manager: automatisch losfahren wenn ein Schacht Erz hat
                for i, s in enumerate(shafts):
                    if s.unlocked and s.ore_stored > 0:
                        self.state = "going_down"
                        self.target_shaft = i
                        break

        elif self.state == "going_down":
            target_y = float(self.shaft_ys[self.target_shaft])
            if self.y < target_y:
                self.y = min(self.y + LIFT_SPEED * dt, target_y)
            else:
                self.y = target_y
                self.state = "collecting"
                self.collect_timer = 0.3    # Kurze Pause

        elif self.state == "collecting":
            self.collect_timer -= dt
            if self.collect_timer <= 0:
                shaft = shafts[self.target_shaft]
                # Letztes Upgrade: alle Schächte auf einmal
                if self.upgrade_level >= len(LIFT_CAPACITY_UPGRADES):
                    for s in shafts:
                        if s.unlocked:
                            take = min(s.ore_stored, self.capacity - self.ore)
                            s.ore_stored -= take
                            self.ore += take
                else:
                    take = min(shaft.ore_stored, self.capacity - self.ore)
                    shaft.ore_stored -= take
                    self.ore += take

                # Nächsten Schacht oder hochfahren?
                next_shaft = self._find_next_shaft(shafts)
                if next_shaft is not None and not self.is_full():
                    self.target_shaft = next_shaft
                    self.state = "going_down"
                else:
                    self.state = "going_up"

        elif self.state == "going_up":
            if self.y > self.top_y:
                self.y = max(self.y - LIFT_SPEED * dt, float(self.top_y))
            else:
                self.y = float(self.top_y)
                self.state = "unloading"
                self.collect_timer = 0.4

        elif self.state == "unloading":
            self.collect_timer -= dt
            if self.collect_timer <= 0:
                coins_earned = self.ore   # Erz wird von Lore abgeholt → Münzwert später
                self.ore = 0
                self.state = "idle"

        return coins_earned     # Anzahl Erz (nicht Münzwert – wird in game.py gerechnet)

    def _find_next_shaft(self, shafts):
        """Findet den nächsten Schacht mit Erz unterhalb des aktuellen."""
        for i in range(self.target_shaft + 1, len(shafts)):
            if shafts[i].unlocked and shafts[i].ore_stored > 0:
                return i
        return None

    # ------------------------------------------------------------------ #
    #  Draw
    # ------------------------------------------------------------------ #
    def draw(self, surface):
        # Schiene
        pygame.draw.line(surface, (100, 100, 100),
                         (self.x + self.w // 2, self.top_y),
                         (self.x + self.w // 2, self.bottom_y), 2)

        # Lift-Rechteck
        if self.state in ("going_up", "going_down"):
            color = (80, 180, 255)
        elif self.is_full():
            color = (255, 100, 80)
        else:
            color = (60, 140, 220)

        rect = pygame.Rect(int(self.x), int(self.y) - self.h // 2, self.w, self.h)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (200, 220, 255), rect, 1)

        # Erz-Anzeige
        ore_surf = self.font.render(f"{self.ore}/{self.capacity}", True, (255, 255, 255))
        surface.blit(ore_surf, (self.x, int(self.y) - self.h // 2 - 14))
