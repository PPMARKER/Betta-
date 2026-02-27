import pygame
from ui.base import UIComponent
from core.theme import COLOR_WHITE, COLOR_BTN_NORMAL, COLOR_BTN_HOVER, get_font
class UILabel(UIComponent):
    def __init__(self, x, y, text, size=18, color=COLOR_WHITE, bold=True, center=False):
        self.text, self.size, self.color, self.bold, self.center = text, size, color, bold, center
        self.render_text()
        super().__init__(self.text_surf.get_rect(center=(x,y) if center else (x,y)))
        if not center: self.rect.topleft = (x, y)
    def render_text(self):
        self.text_surf = get_font("Tahoma", self.size, bold=self.bold).render(self.text, True, self.color)
    def set_text(self, text):
        if text != self.text:
            self.text = text; self.render_text()
            c = self.rect.center; self.rect = self.text_surf.get_rect()
            if self.center: self.rect.center = c
    def draw(self, surface):
        if self.visible: surface.blit(self.text_surf, self.rect)
class UIButton(UIComponent):
    def __init__(self, x, y, w, h, text, color=COLOR_BTN_NORMAL, callback=None):
        super().__init__((x, y, w, h))
        self.text, self.color, self.callback, self.is_hovered = text, color, callback, False
    def handle_event(self, event):
        if not (self.visible and self.enabled): return False
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.callback: self.callback()
            return True
        return False
    def draw(self, surface):
        if not self.visible: return
        c_bg = (70, 120, 220) if self.is_hovered else (50, 90, 160)
        c_border = (255, 255, 255) if self.is_hovered else (180, 180, 180)

        # Outer Glow
        if self.is_hovered:
            for i in range(1, 4):
                pygame.draw.rect(surface, (255, 255, 255, 20), (self.rect.x-i, self.rect.y-i, self.rect.width+i*2, self.rect.height+i*2), border_radius=15+i)

        pygame.draw.rect(surface, c_bg, self.rect, border_radius=15)
        pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=15)

        t = get_font("Tahoma", 14, bold=True).render(self.text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=self.rect.center))
