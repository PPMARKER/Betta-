import pygame
class UIComponent:
    def __init__(self, rect): self.rect, self.visible, self.enabled, self.children = pygame.Rect(rect), True, True, []
    def add_child(self, child): self.children.append(child)
    def handle_event(self, event):
        if not (self.visible and self.enabled): return False
        for child in reversed(self.children):
            if child.handle_event(event): return True
        return False
    def update(self):
        if not self.visible: return
        for child in self.children: child.update()
    def draw(self, surface):
        if not self.visible: return
        for child in self.children: child.draw(surface)
class UIPanel(UIComponent):
    def __init__(self, rect, bg_color=None, border_color=None, border_width=0, border_radius=0):
        super().__init__(rect)
        self.bg_color, self.border_color, self.border_width, self.border_radius = bg_color, border_color, border_width, border_radius
    def draw(self, surface):
        if not self.visible: return
        if self.bg_color: pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        if self.border_color and self.border_width > 0: pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=self.border_radius)
        super().draw(surface)
