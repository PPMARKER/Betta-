import pygame, os, time, random, math
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.theme import COLOR_WHITE, COLOR_GOLD, COLOR_UI_BG, get_font
from core.game_state import game_state
from managers.tank_scene import TankScene
from managers.asset_manager import assets
from entities.fish import Fish
import managers.gl_manager as gl_mod

class BreedingScene(TankScene):
    def __init__(self, scene_manager=None):
        super().__init__(scene_manager)
        self.btn_tank_switch.text = "Tank 1"
        self.btn_tank_switch.callback = self.go_back_to_main
        self.fishes = []
        self.eggs = []
        self.breeding_start_time = 0
        self.breeding_in_progress = False
        self.eggs_spawned = False

    def go_back_to_main(self):
        if hasattr(self, 'sm') and self.sm:
            self.sm.change_scene(self.sm.tank_scene)

    def update(self):
        super().update()

        males = [f for f in self.fishes if f.gender == "Male" and not f.age == 0]
        females = [f for f in self.fishes if f.gender == "Female" and not f.age == 0]

        if len(males) >= 1 and len(females) >= 1:
            if not self.breeding_in_progress and not self.eggs_spawned:
                self.breeding_in_progress = True
                self.breeding_start_time = time.time()
        else:
            if not self.eggs_spawned:
                self.breeding_in_progress = False

        now = time.time()
        if self.breeding_in_progress and now - self.breeding_start_time > 20:
            self.spawn_eggs()
            self.breeding_in_progress = False
            self.eggs_spawned = True

        remaining_eggs = []
        for x, y, t in self.eggs:
            if now - t > 10:
                self.hatch_baby(x, y)
            else:
                remaining_eggs.append((x, y, t))
        self.eggs = remaining_eggs

    def spawn_eggs(self):
        for _ in range(10):
            x = random.randint(200, SCREEN_WIDTH - 200)
            y = random.randint(130, 160)
            self.eggs.append((x, y, time.time()))

    def hatch_baby(self, x, y):
        baby = Fish()
        baby.x, baby.y = x, y
        baby.age = 0
        baby.growth_scale = 0.2
        baby.update_size()
        self.fishes.append(baby)

    def draw(self, _surface):
        super().draw(_surface)
        for x, y, t in self.eggs:
            pygame.draw.circle(self.ui_surf, (255, 255, 255, 150), (x, y), 5)
            pygame.draw.circle(self.ui_surf, (200, 255, 200, 200), (x, y), 3)

        fs = get_font("Tahoma", 24, bold=True)
        status_txt = "Breeding Tank"
        if self.breeding_in_progress:
            elapsed = time.time() - self.breeding_start_time
            status_txt = f"Breeding... {int(20 - elapsed)}s"
        elif self.eggs:
            status_txt = "Eggs hatching..."

        txt = fs.render(status_txt, True, COLOR_WHITE)
        self.ui_surf.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 100))
