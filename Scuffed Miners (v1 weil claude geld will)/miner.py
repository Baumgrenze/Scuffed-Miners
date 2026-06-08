import pygame

MINE_COOLDOWN = 5.0  # Sekunden pro Erz pro Miner

class Miner:
    def __init__(self):
        self.timer = 0.0        # Wie lange schon am warten/minen
        self.ready = False      # Bereit zum Klicken (wenn kein Manager)
        self.mining = False     # Gerade am Minen

    def update(self, dt, has_manager):
        """
        Mit Manager: startet automatisch, laeuft endlos.
        Ohne Manager: wartet auf Klick, fuehrt dann einmal den Cooldown durch.
        """
        if self.mining:
            self.timer += dt
            if self.timer >= MINE_COOLDOWN:
                self.timer = 0.0
                self.mining = False
                self.ready = True
                if has_manager:
                    self.mining = True
                    self.ready = False
                return True
        else:
            if has_manager:
                self.mining = True
                self.ready = False
                self.timer = 0.0
        return False

    def click(self):
        """Spieler klickt manuell - startet Mining wenn bereit oder noch nie gestartet."""
        if not self.mining:
            self.mining = True
            self.ready = False
            self.timer = 0.0

    def draw(self, surface, x, y, index):
        """Zeichnet den Miner als kleines Rechteck + Progressbar darunter."""
        color = (255, 220, 50) if not self.mining else (200, 140, 30)
        mx = x + 40 + index * 28
        rect = pygame.Rect(mx, y + 5, 22, 22)
        pygame.draw.rect(surface, color, rect)

        # Progressbar (nur wenn am Minen)
        if self.mining:
            bar_x = mx
            bar_y = y + 29        # Direkt unter dem Miner-Rechteck
            bar_w = 22
            bar_h = 5

            # Hintergrund
            pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))

            # Fortschritt (0.0 bis 1.0)
            progress = self.timer / MINE_COOLDOWN
            fill_w = int(bar_w * progress)
            if fill_w > 0:
                pygame.draw.rect(surface, (80, 220, 100), (bar_x, bar_y, fill_w, bar_h))
