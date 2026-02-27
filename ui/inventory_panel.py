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
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((10, 20, 30, 200)) # Darker, more glass-like overlay
        surface.blit(ov, (0,0))

        # Main Panel BG with gradient effect
        pygame.draw.rect(surface, (40, 60, 100), self.rect, border_radius=25)
        pygame.draw.rect(surface, (100, 150, 255), self.rect, width=2, border_radius=25)

        # Glassy highlight
        highlight = pygame.Surface((self.rect.width, 50), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), highlight.get_rect(), border_top_left_radius=25, border_top_right_radius=25)
        surface.blit(highlight, self.rect.topleft)

        super().draw(surface)

        ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 40), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 40)
        # Tabs
        for r, label, active in [(ts, "Supplies", self.tab == "Supplies"), (td, "Decorations", self.tab == "Decorations")]:
            c = (70, 130, 230) if active else (50, 70, 120)
            pygame.draw.rect(surface, c, r, border_radius=12)
            if active: pygame.draw.rect(surface, (255, 255, 255), r, width=2, border_radius=12)
            f = get_font("Tahoma", 16, bold=True)
            txt = f.render(label, True, COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=r.center))

        y, mp = 135, pygame.mouse.get_pos()
        if self.tab == "Supplies":
            for k, d in game_state.inventory.items():
                r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 70); h = r.collidepoint(mp)
                c_bg = (80, 110, 160) if h else (60, 80, 120)
                pygame.draw.rect(surface, c_bg, r, border_radius=15)
                if h: pygame.draw.rect(surface, (255, 215, 0), r, width=2, border_radius=15)

                pygame.draw.circle(surface, (255,255,255), (r.x+45, r.centery), 22)
                pygame.draw.circle(surface, d["color"], (r.x+45, r.centery), 20)

                surface.blit(get_font("Tahoma", 20, bold=True).render(d["name"], True, COLOR_WHITE), (r.x+90, r.centery-12))
                surface.blit(get_font("Tahoma", 20, bold=True).render(f"{d['qty']} units", True, COLOR_GOLD), (r.right-150, r.centery-12))
                y += 85
        else:
            for i, d in enumerate(game_state.decor_inventory):
                r = pygame.Rect(self.rect.x+40, self.rect.y+y, 620, 70); h = r.collidepoint(mp)
                c_bg = (80, 110, 160) if h else (60, 80, 120)
                pygame.draw.rect(surface, c_bg, r, border_radius=15)
                if h: pygame.draw.rect(surface, (255, 215, 0), r, width=2, border_radius=15)

                img_small = pygame.transform.smoothscale(d["img"], (50, 50))
                surface.blit(img_small, (r.x+20, r.y+10))
                surface.blit(get_font("Tahoma", 20, bold=True).render(d["name"], True, COLOR_WHITE), (r.x+90, r.centery-12))
                y += 85
