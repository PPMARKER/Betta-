import re

def update_inventory():
    with open('ui/inventory_panel.py', 'r') as f:
        content = f.read()

    # Redesign draw method for better look
    draw_old = """    def draw(self, surface):
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
                y += 100"""

    draw_new = """    def draw(self, surface):
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
                y += 85"""

    content = content.replace(draw_old, draw_new)
    with open('ui/inventory_panel.py', 'w') as f:
        f.write(content)

def update_shop():
    with open('ui/shop_panel.py', 'r') as f:
        content = f.read()

    draw_old = """    def draw(self, surface):
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
            surface.blit(p, (r.centerx - p.get_width()//2, r.bottom-40))"""

    draw_new = """    def draw(self, surface):
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
            surface.blit(price_txt, price_txt.get_rect(center=(r.centerx, r.bottom-40)))"""

    content = content.replace(draw_old, draw_new)
    with open('ui/shop_panel.py', 'w') as f:
        f.write(content)

update_inventory()
update_shop()
