"""
ui.py — Wiederverwendbare UI-Elemente.

Wie ein UI-Prefab
"""

import pygame


class Button:
    """
    Einfacher klickbarer Button mit Hover-Effekt.

    Wird in game.py erstellt und in visuals nicht direkt verwendet —
    damit bleibt die Spiellogik (wann welcher Button aktiv ist) in game.py.
    """
    def __init__(self, x, y, w, h, text, color=(70, 130, 80), font_size=19):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = text
        self.color       = color
        self.hover_color = tuple(min(c + 35, 255) for c in color)
        self.font        = pygame.font.SysFont(None, font_size)

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.color #collide schaut ob maus auf button ist
        pygame.draw.rect(surface, color, self.rect, border_radius=3)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=3)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)) #checkt ob maus auf button ist
