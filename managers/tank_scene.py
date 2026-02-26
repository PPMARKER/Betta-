import pygame, os, time
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TRASH_RECT_COORDS, QUARANTINE_RECT_COORDS
from core.theme import COLOR_DEEP_BLUE, COLOR_OCEAN_BLUE, COLOR_WHITE, COLOR_GOLD, COLOR_UI_BG, get_font
from core.game_state import game_state
from managers.scene_manager import Scene; from managers.ui_manager import UIManager; from managers.asset_manager import assets
from entities.fish import Fish; from entities.food import Food; from entities.decoration import Decoration; from managers.light_manager import LightManager
import managers.gl_manager as gl_mod

class TankScene(Scene):
    def __init__(self):
        self.ui_manager = UIManager(on_decor_pickup=self.on_decor_pickup)
        self.light_manager = LightManager()
        self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor = [Fish(), Fish()], [], [], None, None
        self.trash_rect, self.quarantine_rect = pygame.Rect(*TRASH_RECT_COORDS), pygame.Rect(*QUARANTINE_RECT_COORDS)
        self.ui_manager.hud.add_button(150, 820, 120, 50, "SHOP", self.ui_manager.show_shop)
        self.ui_manager.hud.add_button(280, 820, 120, 50, "INVENTORY", self.ui_manager.show_inventory)
        self.ui_manager.hud.add_button(410, 820, 120, 50, "SPECIES", lambda: None)
        self.ui_manager.hud.add_button(20, 820, 120, 50, "MENU", lambda: None)
        self.ui_manager.hud.add_button(1050, 20, 120, 45, "More Tank", lambda: None, 'top')
        self.ui_manager.hud.add_button(1180, 20, 120, 45, "Sell Tank", lambda: None, 'top')
        self.ui_manager.hud.add_button(1310, 20, 110, 45, "Breed", lambda: None, 'top')

        # Reuse UI surface to avoid memory leaks in GL texture cache
        self.ui_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def on_decor_pickup(self, d):
        self.dragging_decor = Decoration(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], d["img"], d["name"], scale=d.get("scale", 1.0), original_img=d.get("original_img", d["img"]))

    def handle_event(self, e):
        if self.ui_manager.handle_event(e): return
        mp = pygame.mouse.get_pos()
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                if self.dragging_decor: self.decor_objects.append(self.dragging_decor); self.dragging_decor = None
                elif game_state.selected_slot != -1 and game_state.quick_items[game_state.selected_slot]:
                    it = game_state.quick_items[game_state.selected_slot]; d = game_state.inventory[it]
                    if d["qty"] > 0:
                        if it in ["food_p", "food_m"]: self.foods.append(Food(mp[0], mp[1], 'pellet' if it == "food_p" else 'moina')); d["qty"] -= 1
                        elif it == "med":
                            for f in self.fishes:
                                if f.rect.collidepoint(mp) and f.is_sick and not f.is_dead and self.quarantine_rect.colliderect(f.rect): f.is_sick, f.in_quarantine, d["qty"] = False, False, d["qty"] - 1; break
                else:
                    h = None
                    for f in reversed(self.fishes):
                        if f.rect.collidepoint(mp): h = f; break
                    if h: self.dragging_fish = h; h.original_pos, h.is_dragging = (h.x, h.y), True
                    else:
                        hd = None
                        for o in reversed(self.decor_objects):
                            if o.get_rect().collidepoint(mp): hd = o; break
                        if hd: self.dragging_decor = hd; self.decor_objects.remove(hd)
            elif e.button == 3:
                if self.dragging_fish: self.dragging_fish.x, self.dragging_fish.y, self.dragging_fish.is_dragging = self.dragging_fish.original_pos[0], self.dragging_fish.original_pos[1], False; self.dragging_fish = None
                game_state.selected_slot = -1
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.dragging_fish:
            if self.dragging_fish.is_dead:
                if self.trash_rect.collidepoint(mp): self.dragging_fish.to_be_removed = True
            else: self.dragging_fish.in_quarantine = self.quarantine_rect.collidepoint(mp)
            self.dragging_fish.is_dragging, self.dragging_fish = False, None
        elif e.type == pygame.KEYDOWN:
            if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]: game_state.selected_slot = e.key - pygame.K_1
            if e.key == pygame.K_ESCAPE:
                if self.dragging_decor: self.decor_objects.append(self.dragging_decor); self.dragging_decor = None
                game_state.selected_slot = -1
            if self.dragging_decor:
                if e.key == pygame.K_q: self.dragging_decor.update_scale(self.dragging_decor.scale - 0.1)
                elif e.key == pygame.K_e: self.dragging_decor.update_scale(self.dragging_decor.scale + 0.1)

    def update(self):
        gl_mod.gl_manager.update_time(1.0 / 60.0)
        mp = pygame.mouse.get_pos()
        if self.dragging_fish: self.dragging_fish.x, self.dragging_fish.y = mp[0]-self.dragging_fish.size_w/2, mp[1]-self.dragging_fish.size_h/2; self.dragging_fish.rect.topleft = (self.dragging_fish.x, self.dragging_fish.y)
        if self.dragging_decor: self.dragging_decor.x, self.dragging_decor.y = mp
        for f in self.fishes: f.update_stats(); f.move(self.fishes, self.foods)
        self.fishes = [f for f in self.fishes if not f.to_be_removed]
        for f in self.foods: f.update(self.fishes)
        self.foods = [f for f in self.foods if not f.eaten]
        self.ui_manager.update()
        self.light_manager.update()

    def draw(self, _surface):
        # 1. Background
        bg = assets.load_image(os.path.join("asset", "Tank", "Tank.png"), alpha=True)
        if bg: gl_mod.gl_manager.draw_texture(bg, 0, 0)

        # 2. Decorations
        for o in self.decor_objects: o.draw(None)

        # 3. Foods
        for f in self.foods: f.draw(None)

        # 4. Fishes
        for f in self.fishes: f.draw(None)

        # 5. Light (Additive blending for realism)
        self.light_manager.draw(None)

        # 6. UI (Rendered to a surface first)
        self.ui_surf.fill((0, 0, 0, 0))

        # Scene specific UI
        med = assets.load_image(os.path.join("asset", "Ui", "medic_tank.png"), scale=(300, 180))
        if med: self.ui_surf.blit(med, self.quarantine_rect.topleft)
        pygame.draw.rect(self.ui_surf, (80,80,80), self.trash_rect, border_radius=15)
        pygame.draw.rect(self.ui_surf, (220,50,50), self.trash_rect, width=4, border_radius=15)
        self.ui_surf.blit(get_font("Tahoma", 18, bold=True).render("TRASH", True, COLOR_WHITE), (self.trash_rect.x+18, self.trash_rect.y+40))

        if self.dragging_decor:
            t = get_font("Tahoma", 16, bold=True).render("Q/E to Scale, Click to Place", True, COLOR_WHITE)
            self.ui_surf.blit(t, (SCREEN_WIDTH//2-t.get_width()//2, 100))

        self.ui_manager.draw(self.ui_surf)

        if game_state.selected_slot != -1 and game_state.quick_items[game_state.selected_slot]:
            k = game_state.quick_items[game_state.selected_slot]
            if game_state.inventory[k]["qty"] > 0:
                mp = pygame.mouse.get_pos(); pygame.draw.circle(self.ui_surf, game_state.inventory[k]["color"], mp, 8); pygame.draw.circle(self.ui_surf, COLOR_WHITE, mp, 8, 2)

        self.draw_fish_popups(self.ui_surf)

        # Draw the whole UI surface via GL
        gl_mod.gl_manager.draw_texture(self.ui_surf, 0, 0, dynamic=True)

    def draw_fish_popups(self, surface):
        if self.ui_manager.shop.visible or self.ui_manager.inventory.visible or self.dragging_fish or self.dragging_decor: return
        mp = pygame.mouse.get_pos(); h = None
        for f in self.fishes:
            if f.rect.collidepoint(mp) and not f.is_dead: h = f; break
        if h:
            pw, ph = 210, 125; pr = pygame.Rect(mp[0]+15, mp[1]+15, pw, ph)
            if pr.right > SCREEN_WIDTH: pr.x = mp[0]-pw-15
            if pr.bottom > SCREEN_HEIGHT: pr.y = mp[1]-ph-15
            bg = pygame.Surface((pw, ph), pygame.SRCALPHA); pygame.draw.rect(bg, COLOR_UI_BG, (0, 0, pw, ph), border_radius=8); surface.blit(bg, pr.topleft)
            pygame.draw.rect(surface, COLOR_GOLD, pr, 2, border_radius=8)
            fs = get_font("Tahoma", 14, bold=True)
            surface.blit(fs.render(f"Age: {h.age} Days", True, COLOR_WHITE), (pr.x+12, pr.y+12))
            sc = (255, 50, 50) if h.is_sick else (50, 255, 50)
            st = fs.render("HEALTH: ", True, COLOR_WHITE)
            surface.blit(st, (pr.x+12, pr.y+36))
            surface.blit(fs.render("SICK" if h.is_sick else "HEALTHY", True, sc), (pr.x+12+st.get_width(), pr.y+36))
            surface.blit(fs.render("HP:", True, COLOR_WHITE), (pr.x+12, pr.y+66))
            pygame.draw.rect(surface, (80, 0, 0), (pr.x+85, pr.y+69, 100, 10))
            pygame.draw.rect(surface, (0, 255, 0), (pr.x+85, pr.y+69, 100*(h.health/100), 10))
            surface.blit(fs.render("Hunger:", True, COLOR_WHITE), (pr.x+12, pr.y+90))
            pygame.draw.rect(surface, (80, 40, 0), (pr.x+85, pr.y+93, 100, 10))
            pygame.draw.rect(surface, (255, 165, 0), (pr.x+85, pr.y+93, 100*(h.hunger/100), 10))
