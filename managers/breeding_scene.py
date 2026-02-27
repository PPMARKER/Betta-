import pygame, os, time, random, math
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TRASH_RECT_COORDS
from core.theme import COLOR_WHITE, COLOR_GOLD, COLOR_UI_BG, get_font
from core.game_state import game_state
from managers.scene_manager import Scene
from managers.ui_manager import UIManager
from managers.asset_manager import assets
from entities.fish import Fish
from entities.decoration import Decoration
from managers.light_manager import LightManager
import managers.gl_manager as gl_mod

class BreedingScene(Scene):
    def __init__(self, scene_manager):
        self.sm = scene_manager
        self.ui_manager = UIManager()
        self.light_manager = LightManager()
        self.fishes = [] # Fishes currently in breeding tank
        self.eggs = [] # List of (x, y, creation_time)
        self.babies = [] # Baby fish entities

        # UI Setup
        self.ui_manager.hud.add_button(20, 20, 120, 50, "BACK", self.go_back, 'top')
        self.ui_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        self.breeding_start_time = 0
        self.breeding_in_progress = False
        self.eggs_spawned = False

    def go_back(self):
        # Move fish back to main tank if needed?
        # Requirement says "ต้องให้ผู้เล่นเป็นคนลากกลับไปตู้เดิมเอง"
        # So we need a way to transport them.
        # I will store them in game_state or pass them back.
        from managers.tank_scene import TankScene
        if isinstance(self.sm.tank_scene, TankScene):
            # Move fishes back to main tank fishes list
            for f in self.fishes:
                f.in_breeding_mode = False
                self.sm.tank_scene.fishes.append(f)
            for b in self.babies:
                b.in_breeding_mode = False
                self.sm.tank_scene.fishes.append(b)
            self.fishes = []
            self.babies = []
            self.sm.change_scene(self.sm.tank_scene)

    def handle_event(self, e):
        if self.ui_manager.handle_event(e): return
        mp = pygame.mouse.get_pos()

        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                # Handle dragging fish in breeding tank
                h = None
                for f in reversed(self.fishes + self.babies):
                    if f.rect.collidepoint(mp): h = f; break
                if h:
                    self.dragging_fish = h
                    h.is_dragging = True
            elif e.button == 3:
                if hasattr(self, 'dragging_fish') and self.dragging_fish:
                    self.dragging_fish.is_dragging = False
                    self.dragging_fish = None

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if hasattr(self, 'dragging_fish') and self.dragging_fish:
                self.dragging_fish.is_dragging = False
                self.dragging_fish = None

    def update(self):
        gl_mod.gl_manager.update_time(1.0 / 60.0)
        mp = pygame.mouse.get_pos()

        if hasattr(self, 'dragging_fish') and self.dragging_fish:
            self.dragging_fish.x, self.dragging_fish.y = mp[0]-self.dragging_fish.size_w/2, mp[1]-self.dragging_fish.size_h/2
            self.dragging_fish.rect.topleft = (self.dragging_fish.x, self.dragging_fish.y)

        for f in self.fishes:
            f.update_stats()
            f.move(self.fishes + self.babies, [])

        for b in self.babies:
            b.update_stats()
            b.move(self.fishes + self.babies, [])

        # Breeding Logic
        males = [f for f in self.fishes if f.gender == "Male"]
        females = [f for f in self.fishes if f.gender == "Female"]

        if len(males) >= 1 and len(females) >= 1:
            if not self.breeding_in_progress and not self.eggs_spawned:
                self.breeding_in_progress = True
                self.breeding_start_time = time.time()
        else:
            if not self.eggs_spawned:
                self.breeding_in_progress = False

        now = time.time()
        # 2 days in game = 20 seconds (based on age logic 1 day = 10s)
        if self.breeding_in_progress and now - self.breeding_start_time > 20:
            self.spawn_eggs()
            self.breeding_in_progress = False
            self.eggs_spawned = True

        # Egg Hatching logic
        remaining_eggs = []
        for x, y, t in self.eggs:
            if now - t > 10: # Hatch after 10s
                self.hatch_baby(x, y)
            else:
                remaining_eggs.append((x, y, t))
        self.eggs = remaining_eggs
        if self.eggs_spawned and not self.eggs and not self.breeding_in_progress:
            # Reset for next cycle if needed, or just let it be
            pass

        self.ui_manager.update()
        self.light_manager.update()

    def spawn_eggs(self):
        # Create egg particles on surface
        for _ in range(10):
            x = random.randint(200, SCREEN_WIDTH - 200)
            y = random.randint(130, 160) # Near surface
            self.eggs.append((x, y, time.time()))

    def hatch_baby(self, x, y):
        baby = Fish()
        baby.x, baby.y = x, y
        baby.age = 0
        baby.growth_scale = 0.2 # Small baby
        baby.update_size()
        self.babies.append(baby)

    def draw(self, _surface):
        gl_mod.gl_manager.clear((20/255, 100/255, 200/255, 1))
        bg = assets.load_image(os.path.join("asset", "Tank", "Tank.png"), alpha=True)
        if bg: gl_mod.gl_manager.draw_texture(bg, 0, 0)

        for f in self.fishes: f.draw(None)
        for b in self.babies: b.draw(None)

        # Draw Eggs (bubbles/particles)
        for x, y, t in self.eggs:
            # Bubble effect
            pygame.draw.circle(self.ui_surf, (255, 255, 255, 150), (x, y), 5)
            pygame.draw.circle(self.ui_surf, (200, 255, 200, 200), (x, y), 3)

        self.light_manager.draw(None)

        self.ui_surf.fill((0, 0, 0, 0))
        # Draw status
        fs = get_font("Tahoma", 24, bold=True)
        status_txt = "Waiting for pair..."
        if self.breeding_in_progress:
            elapsed = time.time() - self.breeding_start_time
            status_txt = f"Breeding... {int(20 - elapsed)}s"
        elif self.eggs:
            status_txt = "Eggs hatching..."
        elif self.eggs_spawned and not self.eggs:
            status_txt = "Breeding Complete!"

        txt = fs.render(status_txt, True, COLOR_WHITE)
        self.ui_surf.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))

        self.ui_manager.draw(self.ui_surf)
        gl_mod.gl_manager.draw_texture(self.ui_surf, 0, 0, dynamic=True)
