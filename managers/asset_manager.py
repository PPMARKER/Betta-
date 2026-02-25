import pygame
import os
class AssetManager:
    def __init__(self):
        self.images = {}
        self.decor_previews = {}
    def load_image(self, path, scale=None, alpha=True):
        if (path, scale) in self.images: return self.images[(path, scale)]
        try:
            if os.path.exists(path):
                img = pygame.image.load(path)
                img = img.convert_alpha() if alpha else img.convert()
                if scale: img = pygame.transform.scale(img, scale)
                self.images[(path, scale)] = img
                return img
        except: pass
        return self.get_placeholder(scale)
    def get_placeholder(self, scale=None):
        size = scale if scale else (100, 100)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 200, 200, 150), (0, 0, size[0], size[1]))
        pygame.draw.line(surf, (255, 0, 0), (0, 0), size, 2)
        return surf
    def get_decor_preview(self, path):
        if path not in self.decor_previews:
            img = self.load_image(path)
            self.decor_previews[path] = pygame.transform.smoothscale(img, (80, 80))
        return self.decor_previews[path]
assets = AssetManager()
