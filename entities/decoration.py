import pygame
import managers.gl_manager as gl_mod

class Decoration:
    def __init__(self, x, y, img, name, scale=1.0, original_img=None):
        self.x, self.y, self.img, self.name, self.scale = x, y, img, name, scale
        self.original_img = original_img if original_img else img

    def update_scale(self, new_scale):
        self.scale = max(0.1, min(5.0, new_scale))
        w, h = self.original_img.get_size()
        self.img = pygame.transform.smoothscale(self.original_img, (int(w * self.scale), int(h * self.scale)))

    def draw(self, surface):
        rect = self.img.get_rect(midbottom=(self.x, self.y))
        gl_mod.gl_manager.draw_texture(self.img, rect.x, rect.y)

    def get_rect(self):
        return self.img.get_rect(midbottom=(self.x, self.y))
