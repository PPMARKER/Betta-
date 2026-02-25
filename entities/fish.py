import pygame, random, math, time, os
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, QUARANTINE_RECT_COORDS
from core.theme import FISH_COLORS, COLOR_WHITE
from managers.asset_manager import assets
class Fish:
    def __init__(self):
        self.x, self.y = random.randint(200, SCREEN_WIDTH - 400), random.randint(250, SCREEN_HEIGHT - 350)
        self.angle = random.uniform(0, math.pi * 2)
        self.max_speed = random.uniform(1.8, 2.5)
        self.steering_force, self.vel_x, self.vel_y = 0.05, 0, 0
        self.base_color, self.last_color = random.choice(FISH_COLORS), None
        self.age, self.health, self.hunger = 1, 100.0, 70.0
        self.age_timer, self.hunger_timer, self.sickness_timer = time.time(), time.time(), 0
        self.growth_scale = 0.6
        self.update_size()
        self.bob_timer, self.is_dragging, self.is_sick, self.in_quarantine, self.is_dead, self.to_be_removed = random.uniform(0, 100), False, False, False, False, False
        self.image_right, self.image_left = None, None
        self.quarantine_rect = pygame.Rect(*QUARANTINE_RECT_COORDS)
    def update_size(self):
        self.size_w, self.size_h = int(120 * self.growth_scale), int(75 * self.growth_scale)
        self.rect = pygame.Rect(self.x, self.y, self.size_w, self.size_h)
        self.last_color = None
    def update_stats(self):
        if self.is_dead: return
        now = time.time()
        if now - self.age_timer > 10:
            if self.age < 15: self.age += 1; self.growth_scale = min(1.2, 0.6 + (self.age * 0.04)); self.update_size()
            self.age_timer = now
        if now - self.hunger_timer > 2:
            self.hunger -= 3
            if self.hunger < 0: self.hunger = 0
            self.hunger_timer = now
        if self.hunger == 0 and not self.is_sick and now - self.sickness_timer > 1.0:
            if random.random() < 0.15: self.is_sick = True
            self.sickness_timer = now
        if self.hunger == 0 or self.is_sick:
            self.health -= 0.05
            if self.health <= 0: self.health, self.is_dead = 0, True
        elif self.hunger > 60 and not self.is_sick: self.health += 0.05
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
        if self.in_quarantine:
            ll, lr = self.quarantine_rect.left + 10, self.quarantine_rect.right - self.size_w - 10
            tt, tb = self.quarantine_rect.top + 20, self.quarantine_rect.bottom - self.size_h - 10
            self.x, self.y = max(ll, min(lr, self.x)), max(tt, min(tb, self.y))
            if self.x <= ll + 10: ax = 1
            elif self.x >= lr - 10: ax = -1
            if self.y <= tt + 10: ay = 1
            elif self.y >= tb - 10: ay = -1
        else:
            margin = 150
            if self.x < margin: ax = 1
            elif self.x > SCREEN_WIDTH - margin - self.size_w: ax = -1
            if self.y < 120: ay = 1
            elif self.y > 650 - self.size_h: ay = -1
        if ax != 0 or ay != 0: t_angle, self.steering_force = math.atan2(ay, ax), 0.15 if self.in_quarantine else 0.12
        else:
            self.steering_force, target_food = 0.05, None
            if not self.is_sick and self.hunger < 95 and foods:
                min_d = float('inf')
                for f in foods:
                    d = math.hypot(f.x - (self.x + self.size_w / 2), f.y - (self.y + self.size_h / 2))
                    if d < min_d: min_d, target_food = d, f
            if target_food:
                cur_speed = self.max_speed * 1.5
                dx, dy = target_food.x - (self.x + self.size_w / 2), target_food.y - (self.y + self.size_h / 2)
                t_angle = math.atan2(dy, dx)
                if math.hypot(dx, dy) < 40: target_food.eaten, self.hunger = True, min(100, self.hunger + 25)
            else: self.angle += random.uniform(-0.05, 0.05); t_angle = self.angle
        px, py = 0, 0
        for other in all_fishes:
            if other != self and not other.is_dragging and not other.is_dead:
                d = math.hypot((self.x + self.size_w/2) - (other.x + other.size_w/2), (self.y + self.size_h/2) - (other.y + other.size_h/2))
                if 0 < d < (self.size_w + other.size_w) * 0.4: px += (self.x - other.x)/d; py += (self.y - other.y)/d
        self.angle += ((t_angle - self.angle + math.pi) % (2 * math.pi) - math.pi) * self.steering_force
        self.vel_x += (math.cos(self.angle) * cur_speed - self.vel_x) * 0.1
        self.vel_y += (math.sin(self.angle) * (cur_speed * 0.5) - self.vel_y) * 0.1
        self.x, self.y = self.x + self.vel_x + px*1.5, self.y + self.vel_y + py*1.5
        self.bob_timer += 0.05; self.y += math.sin(self.bob_timer) * 0.2
        self.rect.topleft = (self.x, self.y)
    def draw(self, surface):
        t_color = self.base_color
        if self.is_dead: t_color = (-1, -1, -1)
        elif self.is_sick: t_color = tuple(int((c + 200)/2) for c in self.base_color)
        if self.last_color != t_color:
            self.last_color = t_color
            orig = assets.load_image(os.path.join("asset", "Fish", "ลอง.png"))
            if orig:
                temp = pygame.transform.scale(orig, (self.size_w, self.size_h))
                if self.is_dead:
                    try: temp = pygame.transform.grayscale(temp)
                    except: temp.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                else: temp.fill(t_color, special_flags=pygame.BLEND_RGB_MULT)
                self.image_right = temp.copy(); self.image_left = pygame.transform.flip(temp, True, False)
        if self.image_right:
            img = self.image_right if self.vel_x > 0 else self.image_left
            if self.is_dead: img = pygame.transform.flip(img, False, True)
            if self.is_dragging: img = img.copy(); img.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, (self.x, self.y))
        else: pygame.draw.ellipse(surface, (128,128,128) if self.is_dead else t_color, self.rect)
