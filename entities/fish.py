import pygame, random, math, time, os
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.theme import FISH_COLORS, COLOR_WHITE
from managers.asset_manager import assets
import managers.gl_manager as gl_mod

class Fish:
    def __init__(self, gender=None):
        self.x, self.y = random.randint(200, SCREEN_WIDTH - 400), random.randint(250, SCREEN_HEIGHT - 350)
        self.angle = random.uniform(0, math.pi * 2)
        self.max_speed = random.uniform(1.8, 2.5)
        self.steering_force, self.vel_x, self.vel_y = 0.05, 0, 0
        self.base_color = random.choice(FISH_COLORS)
        self.gender = gender if gender else random.choice(["Male", "Female"])
        self.age, self.health, self.hunger = 1, 100.0, 70.0
        self.age_timer, self.hunger_timer, self.sickness_timer = time.time(), time.time(), 0
        self.is_treated = False
        self.treatment_timer = 0

        self.growth_scale = 0.6
        self.update_size()
        self.bob_timer, self.is_dragging, self.is_sick, self.is_dead, self.to_be_removed = random.uniform(0, 100), False, False, False, False
        self.in_breeding_mode = False # To be used in Breeding Scene

    def update_size(self):
        self.size_w, self.size_h = int(120 * self.growth_scale), int(75 * self.growth_scale)
        self.rect = pygame.Rect(self.x, self.y, self.size_w, self.size_h)

    def update_stats(self):
        if self.is_dead: return
        now = time.time()

        # Age update
        if now - self.age_timer > 10:
            if self.age < 15:
                self.age += 1
                self.growth_scale = min(1.2, 0.2 + (self.age * 0.08))
                self.update_size()
            self.age_timer = now

        # Hunger update
        if now - self.hunger_timer > 2:
            self.hunger -= 3
            if self.hunger < 0: self.hunger = 0
            self.hunger_timer = now

        # Medicine logic
        if self.is_sick and self.is_treated:
            if now - self.treatment_timer > 10:
                self.is_sick = False
                self.is_treated = False

        # Sickness logic
        if self.hunger == 0 and not self.is_sick and not self.is_treated and now - self.sickness_timer > 1.0:
            if random.random() < 0.15: self.is_sick = True
            self.sickness_timer = now

        # Health logic
        if self.is_sick:
            if not self.is_treated:
                self.health -= 0.05 # Losing HP
            # else: HP stops dropping (is_treated is True)
            if self.health <= 0: self.health, self.is_dead = 0, True
        elif self.hunger == 0:
            self.health -= 0.05
            if self.health <= 0: self.health, self.is_dead = 0, True
        elif self.hunger > 60:
            # Can only heal if not sick
            self.health += 0.05

        self.health = max(0, min(100, self.health))

    def move(self, all_fishes, foods):
        if self.is_dragging: return
        if self.is_dead:
            bot_y = 680 - self.size_h
            if self.y < bot_y: self.y += 1.5
            else: self.y = bot_y
            self.rect.topleft = (self.x, self.y)
            return

        t_angle, cur_speed, ax, ay = self.angle, self.max_speed, 0, 0
        if self.is_sick: cur_speed *= 0.4

        # Boundaries
        margin = 150
        if self.x < margin: ax = 1
        elif self.x > SCREEN_WIDTH - margin - self.size_w: ax = -1
        if self.y < 120: ay = 1
        elif self.y > 650 - self.size_h: ay = -1

        if ax != 0 or ay != 0:
            t_angle, self.steering_force = math.atan2(ay, ax), 0.12
        else:
            self.steering_force, target_food = 0.05, None
            # Can eat if NOT sick OR (is_sick AND is_treated AND 10s passed -> which means is_sick becomes False)
            # Actually user said: "รอสัก10วิ ถึงจะเริ่มกินอาหารแล้วเพิ่มHpได้"
            # So if is_sick and is_treated, it CANNOT eat yet.
            if not self.is_sick and self.hunger < 95 and foods:
                min_d = float('inf')
                for f in foods:
                    d = math.hypot(f.x - (self.x + self.size_w / 2), f.y - (self.y + self.size_h / 2))
                    if d < min_d: min_d, target_food = d, f

            if target_food:
                cur_speed = self.max_speed * 1.5
                dx, dy = target_food.x - (self.x + self.size_w / 2), target_food.y - (self.y + self.size_h / 2)
                t_angle = math.atan2(dy, dx)
                if math.hypot(dx, dy) < 40:
                    target_food.eaten, self.hunger = True, min(100, self.hunger + 25)
            else:
                self.angle += random.uniform(-0.05, 0.05)
                t_angle = self.angle

        px, py = 0, 0
        for other in all_fishes:
            if other != self and not other.is_dragging and not other.is_dead:
                d = math.hypot((self.x + self.size_w/2) - (other.x + other.size_w/2), (self.y + self.size_h/2) - (other.y + other.size_h/2))
                if 0 < d < (self.size_w + other.size_w) * 0.4:
                    px += (self.x - other.x)/d
                    py += (self.y - other.y)/d

        self.angle += ((t_angle - self.angle + math.pi) % (2 * math.pi) - math.pi) * self.steering_force
        self.vel_x += (math.cos(self.angle) * cur_speed - self.vel_x) * 0.1
        self.vel_y += (math.sin(self.angle) * (cur_speed * 0.5) - self.vel_y) * 0.1
        self.x, self.y = self.x + self.vel_x + px*1.5, self.y + self.vel_y + py*1.5
        self.bob_timer += 0.05
        self.y += math.sin(self.bob_timer) * 0.2
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        orig = assets.load_image(os.path.join("asset", "Fish", "ลอง.png"))
        if not orig: return
        
        color_mult = [c/255.0 for c in self.base_color] + [1.0]
        if self.is_dead: 
            color_mult = [0.4, 0.4, 0.4, 1.0]
        elif self.is_sick: 
            if self.is_treated:
                # Tint it slightly blue-ish or green-ish to show it's treated?
                # Or just keep it sick color until 10s.
                color_mult = [(c/255.0 + 0.4)/2.0 for c in self.base_color] + [1.0]
            else:
                color_mult = [(c/255.0 + 0.8)/2.0 for c in self.base_color] + [1.0]
        
        angle = 0
        if self.is_dead: angle = 180
        
        flip_x = self.vel_x < 0
        speed = 12.0 if not self.is_sick else 5.0
        if self.is_dead: speed = 0
        
        gl_mod.gl_manager.draw_fish(orig, self.x, self.y, self.size_w, self.size_h, color=tuple(color_mult), angle=angle, flip_x=flip_x, speed=speed)
