import pygame
import sys

# --- Initialisierung ---
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Farben
WHITE  = (255, 255, 255)
BLUE   = ( 50, 120, 220)
BLACK  = (  0,   0,   0)

# --- Spieler-Klasse (wie ein GameObject in Unity) ---
class Player:
    def __init__(self, x, y):
        self.x = x          # Position X
        self.y = y          # Position Y
        self.width  = 50
        self.height = 50
        self.speed  = 5     # Pixel pro Frame

    def handle_input(self):
        """Liest Tasteneingaben – ähnlich wie Input.GetAxis() in Unity"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def clamp_to_screen(self, screen_w, screen_h):
        """Hält den Spieler innerhalb des Fensters"""
        self.x = max(0, min(self.x, screen_w - self.width))
        self.y = max(0, min(self.y, screen_h - self.height))

    def draw(self, surface):
        """Zeichnet das Rechteck – ähnlich wie der Renderer in Unity"""
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))


# --- Hauptprogramm ---
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minimales Pygame Beispiel")
    clock = pygame.time.Clock()    # Entspricht Time.deltaTime in Unity

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    font = pygame.font.SysFont(None, 28)

    # --- Game Loop (entspricht Update() in Unity) ---
    while True:
        # 1) Events abfangen (Fenster schließen etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 2) Logik aktualisieren
        player.handle_input()
        player.clamp_to_screen(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 3) Rendern
        screen.fill(WHITE)                                   # Hintergrund leeren
        player.draw(screen)                                  # Spieler zeichnen

        hint = font.render("Pfeiltasten zum Bewegen", True, BLACK)
        screen.blit(hint, (10, 10))

        pygame.display.flip()        # Buffer tauschen (wie in Unity das Rendern am Ende)
        clock.tick(FPS)              # Auf 60 FPS begrenzen


if __name__ == "__main__":
    main()
