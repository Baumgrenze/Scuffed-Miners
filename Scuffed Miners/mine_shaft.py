"""
mine_shaft.py — Logik für einen Minenschacht.

UNITY-PARALLEL: MineShaft ist wie ein MonoBehaviour mit update()-Methode.
Der gemeinsame mine_timer ist wie eine coroutine die alle Miner synchron steuert.
"""

import pygame
from miner import Miner

# -----------------------------------------------------------------------
# Spielbalance: auf ~10 Minuten ausgelegt
# -----------------------------------------------------------------------
MINE_COOLDOWN = 2.0  # Sekunden pro Schürfzyklus (alle Miner gleichzeitig)

# Freischaltkosten und Münzwert pro Erz je Schacht (Index = Schacht-Nummer)
SHAFT_COSTS  = [0, 80, 400, 2000]
SHAFT_INCOME = [1,  4,  16,   64]

# Kosten für zusätzliche Miner: base * multiplier^(anzahl-1)
# (Einheitlicher Multiplikator von 2 für bessere Balance)
MINER_BASE_COSTS = [3, 12, 50, 100]
MINER_MULTIPLIER = [2,  2,  2,   2]

MANAGER_COST = 5  # Einmalige Kosten um einen Manager zu kaufen


class MineShaft:
    """
    Verwaltet einen Minenschacht mit seinen Minern und dem gemeinsamen Timer.

    UNITY-PARALLEL: Ähnlich wie ein GameObject mit mehreren Child-GameObjects (Miner).
    """
    def __init__(self, shaft_id, x, y, w, h):
        self.shaft_id    = shaft_id
        self.x, self.y   = x, y
        self.w, self.h   = w, h

        self.unlocked    = (shaft_id == 0)  # Nur Schacht 0 ist am Anfang frei
        self.unlock_cost = SHAFT_COSTS[shaft_id]
        self.ore_value   = SHAFT_INCOME[shaft_id]

        self.miners      = [Miner()]  # Startet mit einem Miner
        self.has_manager = False
        self.ore_stored  = 0

        # Gemeinsamer Timer für ALLE Miner im Schacht → sie minen synchron
        self.mine_timer  = 0.0

        self.font_med   = pygame.font.SysFont(None, 20)
        self.font_small = pygame.font.SysFont(None, 17)

    @property
    def mine_progress(self):
        """Fortschritt des aktuellen Zyklus als Wert 0.0–1.0 (für Progressbar)."""
        return self.mine_timer / MINE_COOLDOWN

    def next_miner_cost(self):
        """Gibt die Kosten für den nächsten Miner zurück, oder None wenn voll."""
        count = len(self.miners)
        if count >= 10:
            return None
        return MINER_BASE_COSTS[self.shaft_id] * (MINER_MULTIPLIER[self.shaft_id] ** (count - 1))

    def unlock(self):       self.unlocked    = True
    def hire_manager(self): self.has_manager = True

    def add_miner(self):
        if len(self.miners) < 10:
            self.miners.append(Miner())
            return True
        return False

    def click_miners(self):
        """Startet alle wartenden Miner bei Klick auf 'Schürfen'."""
        for m in self.miners:
            m.click()

    def update(self, dt):
        """
        UNITY-PARALLEL: Wie MonoBehaviour.Update() — wird jeden Frame aufgerufen.
        dt = Deltazeit in Sekunden seit dem letzten Frame.
        """
        if not self.unlocked:
            return

        # Manager startet alle nicht-aktiven Miner automatisch (kein Klick nötig)
        if self.has_manager:
            for m in self.miners:
                if not m.active:
                    m.start()

        active_miners = [m for m in self.miners if m.active]
        if not active_miners:
            return  # Niemand schürft gerade

        # Gemeinsamer Timer: alle aktiven Miner produzieren gleichzeitig
        self.mine_timer += dt
        if self.mine_timer >= MINE_COOLDOWN:
            self.mine_timer -= MINE_COOLDOWN        # Timer rücksetzen (kein Drift)
            self.ore_stored += len(active_miners)   # Alle produzieren auf einmal

            if not self.has_manager:
                # Ohne Manager: Miner stoppen und auf nächsten Klick warten
                for m in active_miners:
                    m.active = False
                    m.ready  = True

    def draw(self, surface):
        import visuals
        visuals.draw_shaft(surface, self, self.font_med, self.font_small)
