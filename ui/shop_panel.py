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
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((10, 20, 30, 200))
        surface.blit(ov, (0,0))

        # Panel BG
        pygame.draw.rect(surface, (30, 50, 90), self.rect, border_radius=25)
        pygame.draw.rect(surface, (120, 180, 255), self.rect, width=2, border_radius=25)

        super().draw(surface)

        ts, td = pygame.Rect(self.rect.x+30, self.rect.y+75, 180, 35), pygame.Rect(self.rect.x+220, self.rect.y+75, 180, 35)
        for r, label, active in [(ts, "Supplies", self.category == "Food & Medicine"), (td, "Decorations", self.category == "Decorations")]:
            c = (80, 140, 240) if active else (40, 60, 100)
            pygame.draw.rect(surface, c, r, border_radius=10)
            if active: pygame.draw.rect(surface, (255, 255, 255), r, width=2, border_radius=10)
            f = get_font("Tahoma", 16, bold=True)
            txt = f.render(label, True, COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=r.center))

        its = self.get_items()[self.page*3 : self.page*3+3]
        mp = pygame.mouse.get_pos()
        for i, it in enumerate(its):
            r = pygame.Rect(self.rect.x+30+i*220, self.rect.y+120, 205, 300); h = r.collidepoint(mp)
            c_card = (60, 100, 160) if h else (45, 75, 120)
            pygame.draw.rect(surface, c_card, r, border_radius=20)
            pygame.draw.rect(surface, (255, 215, 0) if h else (150, 150, 150), r, width=2 if not h else 3, border_radius=20)

            if it["type"] == "decor":
                prev = assets.get_decor_preview(it["img_path"])
                surface.blit(prev, prev.get_rect(center=(r.centerx, r.y+80)))
            else:
                pygame.draw.circle(surface, (255,255,255), (r.centerx, r.y+80), 42)
                pygame.draw.circle(surface, it["color"], (r.centerx, r.y+80), 40)

            name_txt = get_font("Tahoma", 18, bold=True).render(it["name"], True, COLOR_WHITE)
            surface.blit(name_txt, name_txt.get_rect(center=(r.centerx, r.y+160)))

            price_txt = get_font("Tahoma", 24, bold=True).render(f"{it['price']} G", True, COLOR_GOLD)
            surface.blit(price_txt, price_txt.get_rect(center=(r.centerx, r.bottom-40)))
