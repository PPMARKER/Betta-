import pygame
from ui.base import UIPanel, UIComponent
from ui.components import UIButton, UILabel
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.theme import COLOR_UI_BG, COLOR_GOLD, COLOR_WHITE
from core.game_state import game_state
class QuickSlot(UIComponent):
    def __init__(self, index, x, y, w, h): super().__init__((x, y, w, h)); self.index = index
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if event.button == 1: game_state.selected_slot = self.index; return True
            if event.button == 3: game_state.quick_items[self.index] = None; return True
        return False
    def draw(self, surface):
        sel = (self.index == game_state.selected_slot)
        pygame.draw.rect(surface, (40, 70, 110), self.rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_WHITE if sel else (80, 80, 100), self.rect, width=3 if sel else 1, border_radius=12)
        key = game_state.quick_items[self.index]
        if key and key in game_state.inventory:
            d = game_state.inventory[key]; pygame.draw.circle(surface, d["color"], self.rect.center, 22)
            t = pygame.font.SysFont("Arial", 16, bold=True).render(f"x{d['qty']}", True, COLOR_WHITE)
            surface.blit(t, (self.rect.right - 35, self.rect.bottom - 22))
        surface.blit(pygame.font.SysFont("Arial", 14, bold=True).render(str(self.index + 1), True, (200, 200, 200)), (self.rect.x + 8, self.rect.y + 5))
class HUD(UIPanel):
    def __init__(self):
        super().__init__((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.top_p = UIPanel((0, 0, SCREEN_WIDTH, 90), bg_color=COLOR_UI_BG); self.add_child(self.top_p)
        self.bot_p = UIPanel((0, 780, SCREEN_WIDTH, 120), bg_color=COLOR_UI_BG); self.add_child(self.bot_p)
        self.gold_label = UILabel(820, 28, f"GOLD: {game_state.gold}G", size=28, color=COLOR_GOLD); self.top_p.add_child(self.gold_label)
        for i in range(3): self.bot_p.add_child(QuickSlot(i, 20 + i * 85, 15, 75, 75))
        game_state.events.subscribe("gold_changed", lambda g: self.gold_label.set_text(f"GOLD: {g}G"))
    def add_button(self, x, y, w, h, text, callback, parent='bottom'):
        btn = UIButton(x, y, w, h, text, callback=callback)
        (self.top_p if parent == 'top' else self.bot_p).add_child(btn); return btn
