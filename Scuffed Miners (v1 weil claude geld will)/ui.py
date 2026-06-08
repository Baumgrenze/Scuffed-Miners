import pygame

class Button:
    def __init__(self, x, y, w, h, text, color=(70, 130, 80)):
        self.rect  = pygame.Rect(x, y, w, h)
        self.text  = text
        self.color = color
        self.hover_color = tuple(min(c + 35, 255) for c in color)
        self.font  = pygame.font.SysFont(None, 19)

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        col   = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=3)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=3)
        surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(surf, surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))
