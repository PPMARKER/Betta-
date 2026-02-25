import pygame, os
from ui.base import UIPanel, UIComponent
from ui.components import UIButton, UILabel
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.theme import COLOR_GOLD, COLOR_WHITE, get_font
from core.game_state import game_state
from data.items import SHOP_ITEMS
from managers.asset_manager import assets
class ShopPanel(UIPanel):
    def __init__(self):
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 200, 700, 450)
        super().__init__(rect, bg_color=(25, 55, 100), border_color=COLOR_WHITE, border_width=3, border_radius=25)
        self.category, self.page, self.visible = "Food & Medicine", 0, False
        self.add_child(UILabel(self.rect.x + 40, self.rect.y + 30, "AQUARIUM SHOP", size=32, color=COLOR_GOLD))
        self.add_child(UIButton(self.rect.x + 580, self.rect.y + 30, 40, 40, "<", callback=lambda: setattr(self, 'page', max(0, self.page - 1))))
        self.add_child(UIButton(self.rect.x + 630, self.rect.y + 30, 40, 40, ">", callback=self.next_page))
    def next_page(self):
        m = max(0, (len(self.get_items()) - 1) // 3)
        if self.page < m: self.page += 1
    def get_items(self): return [it for it in SHOP_ITEMS if (it["type"] in ["food", "medicine"] if self.category == "Food & Medicine" else it["type"] == "decor")]
    def handle_event(self, event):
        if not self.visible: return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos): self.visible = False; return True
            ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 30), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 30)
            if ts.collidepoint(event.pos): self.category, self.page = "Food & Medicine", 0; return True
            if td.collidepoint(event.pos): self.category, self.page = "Decorations", 0; return True
            its = self.get_items()[self.page*3 : self.page*3+3]
            for i, it in enumerate(its):
                if pygame.Rect(self.rect.x+30+i*220, self.rect.y+110, 200, 280).collidepoint(event.pos):
                    if game_state.spend_gold(it["price"]):
                        if it["type"] == "decor": game_state.add_decor({"name": it["name"], "img": assets.load_image(it["img_path"]), "scale": 1.0})
                        else: game_state.add_to_inventory(it["id"], it["qty"])
                    return True
        return super().handle_event(event)
    def draw(self, surface):
        if not self.visible: return
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,180)); surface.blit(ov, (0,0))
        super().draw(surface)
        ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 30), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 30)
        pygame.draw.rect(surface, (50,100,180) if self.category == "Food & Medicine" else (30,60,120), ts, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(surface, (50,100,180) if self.category == "Decorations" else (30,60,120), td, border_top_left_radius=10, border_top_right_radius=10)
        f = get_font("Tahoma", 16, bold=True)
        surface.blit(f.render("Supplies", True, COLOR_WHITE), (ts.x+45, ts.y+5))
        surface.blit(f.render("Decorations", True, COLOR_WHITE), (td.x+40, td.y+5))
        its = self.get_items()[self.page*3 : self.page*3+3]
        mp = pygame.mouse.get_pos()
        for i, it in enumerate(its):
            r = pygame.Rect(self.rect.x+30+i*220, self.rect.y+110, 200, 280); h = r.collidepoint(mp)
            pygame.draw.rect(surface, (50,90,150) if h else (40,70,120), r, border_radius=15)
            pygame.draw.rect(surface, COLOR_WHITE, r, width=2 if not h else 4, border_radius=15)
            if it["type"] == "decor": surface.blit(assets.get_decor_preview(it["img_path"]), (r.centerx-40, r.y+40))
            else: pygame.draw.circle(surface, it["color"], (r.centerx, r.y+80), 40)
            surface.blit(get_font("Tahoma", 20, bold=True).render(it["name"], True, COLOR_WHITE), (r.x+20, r.y+140))
            p = get_font("Tahoma", 22, bold=True).render(f"{it['price']}G", True, COLOR_GOLD)
            surface.blit(p, (r.centerx - p.get_width()//2, r.bottom-40))
