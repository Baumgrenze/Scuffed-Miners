import pygame
from miner import Miner

# Exponentiell steigende Kosten und Erträge pro Schacht
SHAFT_COSTS    = [0, 150, 500, 2000]        # Freischaltkosten
SHAFT_INCOME   = [1,   4,  15,   60]        # Erz-Wert in Münzen

# Upgrade-Kosten für mehr Miner (Index = aktuelle Anzahl Miner, d.h. für 2. Miner = [0], usw.)
MINER_UPGRADE_COSTS = [100, 400, 1200, 4000]   # Kosten für Miner 2,3,4,5
MANAGER_COST        = 10                        # Einmalig pro Schacht

class MineShaft:
    def __init__(self, shaft_id, x, y, w, h):
        self.shaft_id    = shaft_id
        self.x, self.y   = x, y
        self.w, self.h   = w, h

        self.unlocked    = (shaft_id == 0)
        self.unlock_cost = SHAFT_COSTS[shaft_id]
        self.ore_value   = SHAFT_INCOME[shaft_id]

        self.miners      = [Miner()]    # Startet mit 1 Miner
        self.has_manager = False
        self.ore_stored  = 0            # Wartet auf Lift-Abholung

        self.font = pygame.font.SysFont(None, 20)

    # ------------------------------------------------------------------ #
    #  Getter für Upgrade-Kosten
    # ------------------------------------------------------------------ #
    def next_miner_cost(self):
        """Kosten für den nächsten Miner (None wenn schon 5)."""
        count = len(self.miners)
        if count >= 5:
            return None
        return MINER_UPGRADE_COSTS[count - 1]

    # ------------------------------------------------------------------ #
    #  Aktionen
    # ------------------------------------------------------------------ #
    def unlock(self):
        self.unlocked = True

    def hire_manager(self):
        self.has_manager = True

    def add_miner(self):
        if len(self.miners) < 5:
            self.miners.append(Miner())
            return True
        return False

    def click_miners(self):
        """Spieler klickt auf den Schacht – alle bereiten Miner starten."""
        for m in self.miners:
            if not m.mining:
                m.click()

    def collect_all_ore(self):
        """Lift holt alles ab – gibt Gesamtwert zurück und leert Lager."""
        value = self.ore_stored * self.ore_value
        self.ore_stored = 0
        return value

    # ------------------------------------------------------------------ #
    #  Update & Draw
    # ------------------------------------------------------------------ #
    def update(self, dt):
        if not self.unlocked:
            return
        for miner in self.miners:
            produced = miner.update(dt, self.has_manager)
            if produced:
                self.ore_stored += 1

    def draw(self, surface):
        # Hintergrundfarbe
        if not self.unlocked:
            color = (60, 60, 60)
        elif self.has_manager:
            color = (40, 80, 130)
        else:
            color = (50, 90, 100)

        pygame.draw.rect(surface, color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, (180, 180, 180), (self.x, self.y, self.w, self.h), 1)

        name = f"Schacht {self.shaft_id + 1}"
        name_surf = self.font.render(name, True, (255, 255, 255))
        surface.blit(name_surf, (self.x + 6, self.y + 5))

        if self.unlocked:
            # Miner zeichnen
            for i, miner in enumerate(self.miners):
                miner.draw(surface, self.x, self.y, i)

            # Lager
            ore_surf = self.font.render(f"Erz: {self.ore_stored}", True, (200, 230, 255))
            surface.blit(ore_surf, (self.x + 6, self.y + self.h - 18))

            # Manager-Status
            mgr_text = "MGR ✓" if self.has_manager else "kein MGR"
            mgr_color = (100, 255, 100) if self.has_manager else (200, 100, 100)
            mgr_surf = self.font.render(mgr_text, True, mgr_color)
            surface.blit(mgr_surf, (self.x + self.w - 60, self.y + 5))
        else:
            cost_surf = self.font.render(f"Kosten: {self.unlock_cost}", True, (180, 180, 180))
            surface.blit(cost_surf, (self.x + 6, self.y + self.h // 2 - 8))
