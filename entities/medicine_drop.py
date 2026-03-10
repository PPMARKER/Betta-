import pygame
from core.theme import COLOR_WHITE

class MedicineDrop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y - 100
        self.current_y = self.start_y
        self.speed = 5
        self.radius = 6
        self.alpha = 255
        self.landed = False
        self.done = False

    def update(self):
        if not self.landed:
            self.current_y += self.speed
            if self.current_y >= self.y:
                self.current_y = self.y
                self.landed = True
        else:
            self.radius += 2
            self.alpha -= 15
            if self.alpha <= 0:
                self.done = True

    def draw(self, surface):
        if self.done: return
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color = (150, 220, 255, self.alpha)
        if not self.landed:
            pygame.draw.circle(s, color, (self.radius, self.radius), self.radius)
        else:
            pygame.draw.circle(s, color, (self.radius, self.radius), self.radius, 2)
        surface.blit(s, (self.x - self.radius, self.current_y - self.radius))
