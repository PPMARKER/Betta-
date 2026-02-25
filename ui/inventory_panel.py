import pygame
from ui.base import UIPanel; from ui.components import UILabel; from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT; from core.theme import COLOR_GOLD, COLOR_WHITE, get_font; from core.game_state import game_state
class InventoryPanel(UIPanel):
    def __init__(self, on_decor_pickup=None):
        super().__init__(pygame.Rect(SCREEN_WIDTH//2-350, SCREEN_HEIGHT//2-250, 700, 500), bg_color=(30,45,80), border_color=COLOR_WHITE, border_width=3, border_radius=25)
        self.tab, self.visible, self.on_decor_pickup = "Supplies", False, on_decor_pickup
        self.add_child(UILabel(self.rect.x+40, self.rect.y+30, "INVENTORY", size=28, color=COLOR_WHITE))
    def handle_event(self, event):
        if not self.visible: return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos): self.visible = False; return True
            ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 30), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 30)
            if ts.collidepoint(event.pos): self.tab = "Supplies"; return True
            if td.collidepoint(event.pos): self.tab = "Decorations"; return True
            y = 120
            if self.tab == "Supplies":
                for k, d in game_state.inventory.items():
                    r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 80)
                    if r.collidepoint(event.pos):
                        if k not in game_state.quick_items: game_state.quick_items[game_state.quick_items.index(None) if None in game_state.quick_items else 0] = k
                        return True
                    y += 100
            else:
                for i, d in enumerate(game_state.decor_inventory):
                    r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 80)
                    if r.collidepoint(event.pos):
                        if self.on_decor_pickup: self.on_decor_pickup(game_state.decor_inventory.pop(i))
                        self.visible = False; return True
                    y += 100
        return super().handle_event(event)
    def draw(self, surface):
        if not self.visible: return
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,180)); surface.blit(ov, (0,0))
        super().draw(surface)
        ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 30), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 30)
        pygame.draw.rect(surface, (50,100,180) if self.tab == "Supplies" else (30,60,120), ts, border_radius=10)
        pygame.draw.rect(surface, (50,100,180) if self.tab == "Decorations" else (30,60,120), td, border_radius=10)
        f = get_font("Tahoma", 16, bold=True)
        surface.blit(f.render("Supplies", True, COLOR_WHITE), (ts.x+45, ts.y+5)); surface.blit(f.render("Decorations", True, COLOR_WHITE), (td.x+40, td.y+5))
        y, mp = 120, pygame.mouse.get_pos()
        if self.tab == "Supplies":
            for k, d in game_state.inventory.items():
                r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 80); h = r.collidepoint(mp)
                pygame.draw.rect(surface, (70,90,130) if h else (50,70,110), r, border_radius=10)
                pygame.draw.circle(surface, d["color"], (r.x+50, r.centery), 25)
                surface.blit(get_font("Tahoma", 24, bold=True).render(d["name"], True, COLOR_WHITE), (r.x+100, r.centery-15))
                surface.blit(get_font("Tahoma", 24).render(f"{d['qty']} units", True, COLOR_GOLD), (r.right-180, r.centery-15))
                y += 100
        else:
            for i, d in enumerate(game_state.decor_inventory):
                r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 80); h = r.collidepoint(mp)
                pygame.draw.rect(surface, (70,90,130) if h else (50,70,110), r, border_radius=10)
                surface.blit(pygame.transform.smoothscale(d["img"], (60,60)), (r.x+20, r.y+10))
                surface.blit(get_font("Tahoma", 24, bold=True).render(d["name"], True, COLOR_WHITE), (r.x+100, r.centery-15))
                y += 100
