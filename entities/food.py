import pygame, random, math, time
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.theme import COLOR_FOOD_PELLETS, COLOR_FOOD_MOINA
import managers.gl_manager as gl_mod

class Food:
    _moina_surface = None
    _pellet_surface = None

    def __init__(self, x, y, type_name):
        self.x, self.y, self.type = x, y, type_name
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = 0.6 if type_name == 'moina' else 0.2
        self.eaten = False
        self.on_bottom = False
        self.bottom_time = None
        self.wiggle_timer = 0
        self.points = [(random.randint(-4, 4), random.randint(-4, 4)) for _ in range(4)]

        if Food._moina_surface is None:
            Food._moina_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(Food._moina_surface, (150, 0, 0), (10, 10), 3)
            # Lines are dynamic, so we might need a separate way for moina or just use a circle for moina too
        
        if Food._pellet_surface is None:
            Food._pellet_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(Food._pellet_surface, COLOR_FOOD_PELLETS, (6, 6), 5)
            pygame.draw.circle(Food._pellet_surface, (100, 50, 10), (6, 6), 5, 1)

    def update(self, fishes):
        margin_x, margin_y_top, margin_y_bot = 160, 130, 630
        if self.type == 'moina':
            flee_x, flee_y, danger = 0, 0, False
            for fish in fishes:
                if fish.is_dead: continue
                dist = math.hypot(fish.x + (fish.size_w / 2) - self.x, fish.y + (fish.size_h / 2) - self.y)
                if dist < 150:
                    flee_x += (self.x - (fish.x + fish.size_w / 2)) / (dist + 1)
                    flee_y += (self.y - (fish.y + fish.size_h / 2)) / (dist + 1)
                    danger = True
            if danger:
                self.angle += ((math.atan2(flee_y, flee_x) - self.angle + math.pi) % (2 * math.pi) - math.pi) * 0.1
                self.speed = 1.1
            else:
                self.angle += random.uniform(-0.1, 0.1)
                self.speed = 0.6
            if self.x <= margin_x or self.x >= SCREEN_WIDTH - margin_x or self.y <= margin_y_top or self.y >= margin_y_bot:
                self.angle = math.atan2(SCREEN_HEIGHT/2 - self.y, SCREEN_WIDTH/2 - self.x)
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed + 0.1
        else:
            self.y += 1.5
            self.x += math.sin(self.wiggle_timer * 0.5) * 0.5
        self.x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.x))
        self.y = max(margin_y_top, min(margin_y_bot, self.y))
        if self.y >= margin_y_bot:
            if not self.on_bottom: self.on_bottom, self.bottom_time = True, time.time()
            if self.bottom_time and time.time() - self.bottom_time > (8 if self.type == 'moina' else 5): self.eaten = True
        self.wiggle_timer += 0.2

    def draw(self, _surface):
        if self.type == 'moina':
            # For moina, we use the static surface for the body
            # and we can ignore the wiggle lines or use a simpler effect to stay at 60 FPS
            gl_mod.gl_manager.draw_texture(Food._moina_surface, self.x - 10, self.y - 10)
        else:
            gl_mod.gl_manager.draw_texture(Food._pellet_surface, self.x - 6, self.y - 6)
