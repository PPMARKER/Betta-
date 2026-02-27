import re

with open('ui/hud.py', 'r') as f:
    content = f.read()

# Replace UIPanel background with image blits in HUD.draw or similar
# Let's override HUD.draw to use assets/Ui/top_Ui.png and bottom_ui.png

hud_draw_method = """    def draw(self, surface):
        from managers.asset_manager import assets
        import os
        top_img = assets.load_image(os.path.join("asset", "Ui", "top_Ui.png"), scale=(SCREEN_WIDTH, 90))
        bot_img = assets.load_image(os.path.join("asset", "Ui", "bottom_ui.png"), scale=(SCREEN_WIDTH, 120))
        if top_img: surface.blit(top_img, (0, 0))
        if bot_img: surface.blit(bot_img, (0, 780))
        super().draw(surface)"""

if 'def draw(self, surface):' not in content:
    content += "\n" + hud_draw_method

# Also make the UIPanels transparent so the image shows through
content = content.replace('bg_color=COLOR_UI_BG', 'bg_color=(0,0,0,0)')

with open('ui/hud.py', 'w') as f:
    f.write(content)

with open('ui/components.py', 'r') as f:
    content = f.read()

# Update UIButton to be more stylish
button_draw_old = """    def draw(self, surface):
        if not self.visible: return
        c = COLOR_BTN_HOVER if self.is_hovered else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, width=2, border_radius=10)
        t = get_font("Tahoma", 18, bold=True).render(self.text, True, COLOR_WHITE)
        surface.blit(t, t.get_rect(center=self.rect.center))"""

button_draw_new = """    def draw(self, surface):
        if not self.visible: return
        c = (60, 100, 150) if self.is_hovered else (40, 70, 110)
        pygame.draw.rect(surface, c, self.rect, border_radius=15)
        pygame.draw.rect(surface, (255, 215, 0) if self.is_hovered else (200, 200, 200), self.rect, width=2, border_radius=15)
        # Glow effect if hovered
        if self.is_hovered:
            glow = pygame.Surface((self.rect.width+6, self.rect.height+6), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 215, 0, 50), glow.get_rect(), border_radius=18)
            surface.blit(glow, (self.rect.x-3, self.rect.y-3))

        t = get_font("Tahoma", 16, bold=True).render(self.text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=self.rect.center))"""

content = content.replace(button_draw_old, button_draw_new)
with open('ui/components.py', 'w') as f:
    f.write(content)
