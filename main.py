import pygame
import random
import os
import math
import time

# --- 1. ตั้งค่าพื้นฐาน ---
pygame.init()
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ocean Tycoon - Drag Medic & Black/White Death")
clock = pygame.time.Clock()

# สีธีม
COLOR_DEEP_BLUE = (10, 35, 66)
COLOR_OCEAN_BLUE = (30, 144, 255)
COLOR_SAND = (244, 164, 96)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_UI_BG = (20, 50, 90, 220)
COLOR_BTN_NORMAL = (40, 90, 150)
COLOR_BTN_HOVER = (60, 120, 200)
COLOR_FOOD_PELLETS = (139, 69, 19)
COLOR_FOOD_MOINA = (255, 50, 50)

FISH_COLORS = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
    (255, 100, 255), (100, 255, 255), (255, 165, 0), (160, 32, 240),
    (240, 230, 140), (0, 255, 127)
]

player_gold = 1000

# --- 2. โหลดภาพ (Assets) ---
try:
    bg_path = os.path.join("asset", "Tank", "Tank.png")
    background = pygame.image.load(bg_path).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background = None

try:
    medic_path = os.path.join("asset", "Ui", "medic_tank.png")
    medic_img = pygame.image.load(medic_path).convert_alpha()
    medic_img = pygame.transform.scale(medic_img, (300, 180))
except:
    medic_img = None

try:
    fish_path = os.path.join("asset", "Fish", "ลอง.png")
    original_fish_img = pygame.image.load(fish_path).convert_alpha()
except:
    original_fish_img = None


def load_decor_img(path):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return img
    except:
        pass
    # Placeholder: green surface
    surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 200, 100, 150), (10, 10, 80, 80))
    pygame.draw.polygon(surf, (200, 255, 200, 200), [(50, 0), (100, 100), (0, 100)])
    return surf


# Cache for shop decoration previews to avoid repeated disk I/O and scaling
shop_decor_previews = {}


def get_shop_preview(path):
    if path not in shop_decor_previews:
        img = load_decor_img(path)
        shop_decor_previews[path] = pygame.transform.smoothscale(img, (80, 80))
    return shop_decor_previews[path]


quarantine_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 710, 300, 180)
trash_rect = pygame.Rect(SCREEN_WIDTH - 130, 650, 100, 100)  # ถังขยะมุมขวาล่าง


# --- 3. คลาสอาหาร ---
class Food:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.type = type_name
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = 0.6 if type_name == 'moina' else 0.2
        self.eaten = False
        self.on_bottom = False
        self.bottom_time = None
        self.wiggle_timer = 0
        self.points = [(random.randint(-4, 4), random.randint(-4, 4)) for _ in range(4)]

    def update(self, fishes):
        margin_x = 160
        margin_y_top = 130
        margin_y_bot = 630

        if self.type == 'moina':
            flee_vector_x, flee_vector_y = 0, 0
            perceived_danger = False
            for fish in fishes:
                if fish.is_dead: continue
                dist = math.hypot(fish.x + (fish.size_w / 2) - self.x, fish.y + (fish.size_h / 2) - self.y)
                if dist < 150:
                    diff_x = self.x - (fish.x + fish.size_w / 2)
                    diff_y = self.y - (fish.y + fish.size_h / 2)
                    flee_vector_x += diff_x / (dist + 1)
                    flee_vector_y += diff_y / (dist + 1)
                    perceived_danger = True

            if perceived_danger:
                target_angle = math.atan2(flee_vector_y, flee_vector_x)
                angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
                self.angle += angle_diff * 0.1
                self.speed = 1.1
            else:
                self.angle += random.uniform(-0.1, 0.1)
                self.speed = 0.6

            if self.x <= margin_x or self.x >= SCREEN_WIDTH - margin_x or self.y <= margin_y_top or self.y >= margin_y_bot:
                center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
                self.angle = math.atan2(center_y - self.y, center_x - self.x)

            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed + 0.1
        else:
            self.y += 1.5
            self.x += math.sin(self.wiggle_timer * 0.5) * 0.5

        self.x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.x))
        self.y = max(margin_y_top, min(margin_y_bot, self.y))

        if self.y >= margin_y_bot:
            if not self.on_bottom:
                self.on_bottom = True
                self.bottom_time = time.time()
            if self.bottom_time and time.time() - self.bottom_time > (8 if self.type == 'moina' else 5):
                self.eaten = True

        self.wiggle_timer += 0.2

    def draw(self, surface):
        if self.type == 'moina':
            offset_y = math.sin(self.wiggle_timer) * 3
            current_points = [(self.x + px, self.y + py + (offset_y if i % 2 == 0 else -offset_y)) for i, (px, py) in
                              enumerate(self.points)]
            if len(current_points) >= 2:
                pygame.draw.lines(surface, COLOR_FOOD_MOINA, False, current_points, 2)
            pygame.draw.circle(surface, (150, 0, 0), (int(self.x), int(self.y)), 3)
        else:
            pygame.draw.circle(surface, COLOR_FOOD_PELLETS, (int(self.x), int(self.y)), 5)
            pygame.draw.circle(surface, (100, 50, 10), (int(self.x), int(self.y)), 5, 1)


foods = []


# --- 4. คลาสสำหรับปุ่ม UI ---
class UIButton:
    def __init__(self, x, y, w, h, text, color=COLOR_BTN_NORMAL):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        draw_color = COLOR_BTN_HOVER if self.is_hovered else self.color
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, width=2, border_radius=10)
        font = pygame.font.SysFont("Tahoma", 18, bold=True)
        text_surf = font.render(self.text, True, COLOR_WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered


# --- 5. คลาสสำหรับตัวปลา ---
class Fish:
    def __init__(self):
        self.x = random.randint(200, SCREEN_WIDTH - 400)
        self.y = random.randint(250, SCREEN_HEIGHT - 350)
        self.angle = random.uniform(0, math.pi * 2)
        self.max_speed = random.uniform(1.8, 2.5)
        self.steering_force = 0.05
        self.vel_x = math.cos(self.angle) * self.max_speed
        self.vel_y = math.sin(self.angle) * self.max_speed

        self.base_color = random.choice(FISH_COLORS)
        self.last_color = None

        self.age = 1
        self.health = 100.0
        self.hunger = 70.0

        self.age_timer = time.time()
        self.hunger_timer = time.time()
        self.sickness_timer = 0

        self.growth_scale = 0.6
        self.update_size()

        self.bob_timer = random.uniform(0, 100)
        self.is_dragging = False
        self.is_sick = False
        self.in_quarantine = False  # สถานะการถูกจับใส่ตู้พยาบาล
        self.is_dead = False
        self.to_be_removed = False
        self.original_pos = (self.x, self.y)

    def update_size(self):
        self.size_w = int(120 * self.growth_scale)
        self.size_h = int(75 * self.growth_scale)
        self.rect = pygame.Rect(self.x, self.y, self.size_w, self.size_h)
        self.last_color = None

    def update_stats(self):
        if self.is_dead:
            return

        now = time.time()

        if now - self.age_timer > 10:
            if self.age < 15:
                self.age += 1
                self.growth_scale = min(1.2, 0.6 + (self.age * 0.04))
                self.update_size()
            self.age_timer = now

        if now - self.hunger_timer > 2:
            self.hunger -= 3
            if self.hunger < 0: self.hunger = 0
            self.hunger_timer = now

        if self.hunger == 0:
            if not self.is_sick and now - self.sickness_timer > 1.0:
                if random.random() < 0.15:
                    self.is_sick = True
                self.sickness_timer = now

        if self.hunger == 0 or self.is_sick:
            self.health -= 0.05
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
        elif self.hunger > 60 and not self.is_sick:
            self.health += 0.05

        self.health = max(0, min(100, self.health))

    def move(self, all_fishes):
        if self.is_dragging: return

        if self.is_dead:
            # จมลงก้นตู้และนิ่งอยู่ตรงนั้น
            bottom_y = 680 - self.size_h
            if self.y < bottom_y:
                self.y += 1.5
            else:
                self.y = bottom_y
            self.rect.topleft = (self.x, self.y)
            return

        target_angle = self.angle
        current_speed = self.max_speed
        avoid_x, avoid_y = 0, 0

        # ปลาป่วยจะว่ายช้าลง (ไม่ว่าจะอยู่ในตู้ไหน)
        if self.is_sick:
            current_speed *= 0.4

        # เช็คขอบเขตการว่าย (ขึ้นอยู่กับว่าถูกจับใส่ Medic Tank หรือไม่)
        if self.in_quarantine:
            # บังคับให้อยู่ในกรอบตู้พยาบาล
            limit_l, limit_r = quarantine_rect.left + 10, quarantine_rect.right - self.size_w - 10
            limit_t, limit_b = quarantine_rect.top + 20, quarantine_rect.bottom - self.size_h - 10

            self.x = max(limit_l, min(limit_r, self.x))
            self.y = max(limit_t, min(limit_b, self.y))

            if self.x <= limit_l + 10:
                avoid_x = 1
            elif self.x >= limit_r - 10:
                avoid_x = -1
            if self.y <= limit_t + 10:
                avoid_y = 1
            elif self.y >= limit_b - 10:
                avoid_y = -1
        else:
            # ขอบเขตตู้ปลาหลัก
            margin = 150
            if self.x < margin:
                avoid_x = 1
            elif self.x > SCREEN_WIDTH - margin - self.size_w:
                avoid_x = -1
            if self.y < 120:
                avoid_y = 1
            elif self.y > 650 - self.size_h:
                avoid_y = -1

        if avoid_x != 0 or avoid_y != 0:
            target_angle = math.atan2(avoid_y, avoid_x)
            self.steering_force = 0.15 if self.in_quarantine else 0.12
        else:
            self.steering_force = 0.05
            target_food = None
            if not self.is_sick and self.hunger < 95 and foods:
                min_dist = float('inf')
                for f in foods:
                    dist = math.hypot(f.x - (self.x + self.size_w / 2), f.y - (self.y + self.size_h / 2))
                    if dist < min_dist:
                        min_dist = dist
                        target_food = f

            if target_food:
                current_speed = self.max_speed * 1.5
                dx = target_food.x - (self.x + self.size_w / 2)
                dy = target_food.y - (self.y + self.size_h / 2)
                target_angle = math.atan2(dy, dx)

                if math.hypot(dx, dy) < 40:
                    target_food.eaten = True
                    self.hunger = min(100, self.hunger + 25)
            else:
                self.angle += random.uniform(-0.05, 0.05)
                target_angle = self.angle

        push_x, push_y = 0, 0
        for other in all_fishes:
            if other != self and not other.is_dragging and not other.is_dead:
                dist = math.hypot((self.x + self.size_w / 2) - (other.x + other.size_w / 2),
                                  (self.y + self.size_h / 2) - (other.y + other.size_h / 2))
                min_safe_dist = (self.size_w + other.size_w) * 0.4
                if 0 < dist < min_safe_dist:
                    push_x += (self.x - other.x) / dist
                    push_y += (self.y - other.y) / dist

        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += angle_diff * self.steering_force

        self.vel_x += (math.cos(self.angle) * current_speed - self.vel_x) * 0.1
        self.vel_y += (math.sin(self.angle) * (current_speed * 0.5) - self.vel_y) * 0.1

        self.x += self.vel_x + (push_x * 1.5)
        self.y += self.vel_y + (push_y * 1.5)

        self.bob_timer += 0.05
        self.y += math.sin(self.bob_timer) * 0.2
        self.rect.topleft = (self.x, self.y)

        # ล็อคขอบเขต (กรณีหลุด)
        if not self.in_quarantine:
            self.x = max(30, min(SCREEN_WIDTH - self.size_w - 30, self.x))
            self.y = max(100, min(680 - self.size_h, self.y))

    def draw(self, surface):
        target_color = self.base_color

        # เซ็ตสีจำลองเพื่อสั่งให้ระบบ Render ภาพใหม่ตอนตาย (ขาวดำ) หรือป่วย (สีซีด)
        if self.is_dead:
            target_color = (-1, -1, -1)  # ค่า dummy ให้รู้ว่าตาย
        elif self.is_sick:
            target_color = (
                int((self.base_color[0] + 200) / 2),
                int((self.base_color[1] + 200) / 2),
                int((self.base_color[2] + 200) / 2)
            )

        # หากสถานะเปลี่ยน จะ Render รูปใหม่
        if self.last_color != target_color:
            self.last_color = target_color
            if original_fish_img:
                temp_surface = pygame.transform.scale(original_fish_img, (self.size_w, self.size_h))

                if self.is_dead:
                    try:
                        # สร้างภาพขาวดำโดยใช้ฟังก์ชันของ Pygame
                        temp_surface = pygame.transform.grayscale(temp_surface)
                    except AttributeError:
                        # ฟอลแบ็กสำหรับ Pygame เวอร์ชันเก่า
                        temp_surface.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                else:
                    # ใส่สีตามปกติ / สีซีดลงตอนป่วย
                    temp_surface.fill(target_color, special_flags=pygame.BLEND_RGB_MULT)

                self.image_right = temp_surface.copy()
                self.image_left = pygame.transform.flip(self.image_right, True, False)

        if original_fish_img:
            img = self.image_right if self.vel_x > 0 else self.image_left
            if self.is_dead:
                img = pygame.transform.flip(img, False, True)  # หงายท้อง

            if self.is_dragging:
                img = img.copy()
                img.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(img, (self.x, self.y))
        else:
            draw_color = (128, 128, 128) if self.is_dead else target_color
            pygame.draw.ellipse(surface, draw_color, self.rect)


# --- ฟังก์ชันวาด Popup ข้อมูลปลา ---
def draw_fish_popup(surface, fish, mouse_pos):
    if fish.is_dead: return

    popup_w, popup_h = 160, 90
    popup_rect = pygame.Rect(mouse_pos[0] + 15, mouse_pos[1] + 15, popup_w, popup_h)

    if popup_rect.right > SCREEN_WIDTH: popup_rect.x = mouse_pos[0] - popup_w - 15
    if popup_rect.bottom > SCREEN_HEIGHT: popup_rect.y = mouse_pos[1] - popup_h - 15

    bg_surface = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 200))
    surface.blit(bg_surface, popup_rect.topleft)
    pygame.draw.rect(surface, (100, 100, 100), popup_rect, 2)

    font_sm = pygame.font.SysFont("Tahoma", 14, bold=True)
    age_txt = font_sm.render(f"Age: {fish.age} Days", True, COLOR_WHITE)
    status_color = (255, 50, 50) if fish.is_sick else (50, 255, 50)
    status_txt = font_sm.render("SICK" if fish.is_sick else "HEALTHY", True, status_color)

    surface.blit(age_txt, (popup_rect.x + 10, popup_rect.y + 10))
    surface.blit(status_txt, (popup_rect.right - status_txt.get_width() - 10, popup_rect.y + 10))

    surface.blit(font_sm.render("HP", True, COLOR_WHITE), (popup_rect.x + 10, popup_rect.y + 35))
    pygame.draw.rect(surface, (100, 0, 0), (popup_rect.x + 35, popup_rect.y + 37, 110, 10))
    pygame.draw.rect(surface, (0, 255, 0), (popup_rect.x + 35, popup_rect.y + 37, 110 * (fish.health / 100), 10))

    surface.blit(font_sm.render("Food", True, COLOR_WHITE), (popup_rect.x + 10, popup_rect.y + 55))
    pygame.draw.rect(surface, (100, 50, 0), (popup_rect.x + 50, popup_rect.y + 57, 95, 10))
    pygame.draw.rect(surface, (255, 165, 0), (popup_rect.x + 50, popup_rect.y + 57, 95 * (fish.hunger / 100), 10))


# --- 6. ระบบ UI & Gameplay ---
my_fishes = [Fish(), Fish()]

show_shop = False
show_supplies = False
shop_category = "Food & Medicine"
shop_page = 0
shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 200, 700, 450)
supplies_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 250, 700, 500)

shop_items = [
    {"name": "Pellets", "price": 50, "qty": 30, "color": COLOR_FOOD_PELLETS, "type": "food", "id": "food_p"},
    {"name": "Moina", "price": 100, "qty": 20, "color": COLOR_FOOD_MOINA, "type": "food", "id": "food_m"},
    {"name": "Medicine", "price": 100, "qty": 10, "color": (50, 255, 50), "type": "medicine", "id": "med"},
    {"name": "Build 1", "price": 200, "type": "decor", "img_path": "asset/build/Build_1.png"},
    {"name": "Build 2", "price": 250, "type": "decor", "img_path": "asset/build/Build_2.png"},
    {"name": "Build 3", "price": 300, "type": "decor", "img_path": "asset/build/Build_3.png"},
    {"name": "Build 4", "price": 350, "type": "decor", "img_path": "asset/build/Build_4.png"},
    {"name": "Build 5", "price": 400, "type": "decor", "img_path": "asset/build/Build_5.png"},
    {"name": "Build 6", "price": 450, "type": "decor", "img_path": "asset/build/Build_6.png"},
    {"name": "Build 7", "price": 500, "type": "decor", "img_path": "asset/build/Build_7.png"},
    {"name": "Build 8", "price": 550, "type": "decor", "img_path": "asset/build/Build_8.png"},
]

is_build_mode = False
selected_decor = None
decor_inventory = []
decor_objects = []

quick_slots = [pygame.Rect(20 + i * 85, 15, 75, 75) for i in range(3)]
selected_slot = -1

inventory = {
    "food_p": {"name": "Pellets", "color": COLOR_FOOD_PELLETS, "qty": 10, "type": "food"},
    "food_m": {"name": "Moina", "color": COLOR_FOOD_MOINA, "qty": 5, "type": "food"},
    "med": {"name": "Medicine", "color": (50, 255, 50), "qty": 2, "type": "medicine"}
}
quick_items = ["food_p", "food_m", "med"]

btn_shop = UIButton(150, 820, 120, 50, "SHOP", color=COLOR_BTN_NORMAL)
btn_supplies = UIButton(280, 820, 120, 50, "SUPPLIES")
btn_build = UIButton(410, 820, 120, 50, "BUILD")
top_buttons = [
    UIButton(1050, 20, 120, 45, "More Tank"),
    UIButton(1180, 20, 120, 45, "Sell Tank"),
    UIButton(1310, 20, 110, 45, "Breed")
]
bottom_buttons = [
    UIButton(20, 820, 120, 50, "MENU"),
    btn_shop,
    btn_supplies,
    btn_build,
    UIButton(540, 820, 120, 50, "SPECIES")
]

dragging_fish = None

# --- 7. Main Loop ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_ui = False

                if show_shop:
                    if shop_rect.collidepoint(mouse_pos):
                        # Tabs
                        tab_supplies = pygame.Rect(shop_rect.x + 30, shop_rect.y + 65, 180, 30)
                        tab_decor = pygame.Rect(shop_rect.x + 220, shop_rect.y + 65, 180, 30)
                        if tab_supplies.collidepoint(mouse_pos):
                            shop_category = "Food & Medicine"
                            shop_page = 0
                        elif tab_decor.collidepoint(mouse_pos):
                            shop_category = "Decorations"
                            shop_page = 0

                        # Pagination buttons
                        btn_prev = pygame.Rect(shop_rect.x + 580, shop_rect.y + 30, 40, 40)
                        btn_next = pygame.Rect(shop_rect.x + 630, shop_rect.y + 30, 40, 40)
                        current_category_items = [it for it in shop_items if (it["type"] in ["food", "medicine"] if shop_category == "Food & Medicine" else it["type"] == "decor")]
                        max_pages = max(0, (len(current_category_items) - 1) // 3)

                        if btn_prev.collidepoint(mouse_pos):
                            shop_page = max(0, shop_page - 1)
                        elif btn_next.collidepoint(mouse_pos):
                            if shop_page < max_pages:
                                shop_page += 1
                        start_idx = shop_page * 3
                        display_items = current_category_items[start_idx:start_idx + 3]

                        for i, item in enumerate(display_items):
                            btn_rect = pygame.Rect(shop_rect.x + 30 + (i * 220), shop_rect.y + 110, 200, 280)
                            if btn_rect.collidepoint(mouse_pos):
                                if player_gold >= item["price"]:
                                    player_gold -= item["price"]
                                    if item["type"] == "decor":
                                        img = load_decor_img(item["img_path"])
                                        decor_inventory.append({"name": item["name"], "img": img, "scale": 1.0})
                                    else:
                                        inventory[item["id"]]["qty"] += item["qty"]
                    else:
                        show_shop = False
                    clicked_ui = True

                elif show_supplies:
                    if supplies_rect.collidepoint(mouse_pos):
                        y_offset = 120
                        # Only show food and medicine
                        for key, data in inventory.items():
                            if data.get("type") not in ["food", "medicine"]: continue
                            item_line = pygame.Rect(supplies_rect.x + 40, supplies_rect.y + y_offset, 620, 80)
                            if item_line.collidepoint(mouse_pos):
                                if key not in quick_items:
                                    if None in quick_items:
                                        quick_items[quick_items.index(None)] = key
                                    else:
                                        quick_items[0] = key
                            y_offset += 100
                    else:
                        show_supplies = False
                    clicked_ui = True

                if not clicked_ui:
                    for i, slot in enumerate(quick_slots):
                        if slot.collidepoint(mouse_pos):
                            selected_slot = i
                            clicked_ui = True

                if not clicked_ui:
                    if btn_shop.rect.collidepoint(mouse_pos):
                        show_shop = True
                        show_supplies = False
                        is_build_mode = False
                        clicked_ui = True
                    elif btn_supplies.rect.collidepoint(mouse_pos):
                        show_supplies = True
                        show_shop = False
                        is_build_mode = False
                        clicked_ui = True
                    elif btn_build.rect.collidepoint(mouse_pos):
                        is_build_mode = True
                        show_shop = False
                        show_supplies = False
                        clicked_ui = True

                if not clicked_ui:
                    for btn in top_buttons + bottom_buttons:
                        if btn.rect.collidepoint(mouse_pos): clicked_ui = True

                if not clicked_ui and is_build_mode:
                    # Check if clicked on decor inventory UI
                    decor_ui_rect = pygame.Rect(30, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 60, 100)
                    if decor_ui_rect.collidepoint(mouse_pos):
                        for i, decor in enumerate(decor_inventory):
                            decor_btn = pygame.Rect(40 + i * 110, SCREEN_HEIGHT - 210, 100, 80)
                            if decor_btn.collidepoint(mouse_pos):
                                selected_decor = decor
                                break
                        clicked_ui = True

                if not clicked_ui:
                    if is_build_mode and selected_decor:
                        # Place decoration
                        img_to_place = selected_decor["img"]
                        scale_to_place = selected_decor.get("scale", 1.0)
                        w, h = img_to_place.get_size()
                        # Cache the scaled image upon placement for better performance
                        scaled_img = pygame.transform.smoothscale(img_to_place, (int(w * scale_to_place), int(h * scale_to_place)))
                        decor_objects.append({
                            "img": scaled_img,
                            "x": mouse_pos[0],
                            "y": mouse_pos[1]
                        })
                        clicked_ui = True
                    elif selected_slot != -1 and quick_items[selected_slot] is not None:
                        item_type = quick_items[selected_slot]
                        item_data = inventory[item_type]
                        if item_data["qty"] > 0:
                            if item_type in ["food_p", "food_m"]:
                                foods.append(
                                    Food(mouse_pos[0], mouse_pos[1], 'pellet' if item_type == "food_p" else 'moina'))
                                item_data["qty"] -= 1
                            elif item_type == "med":
                                # การรักษายา: ตรวจสอบว่าปลาป่วยและถูกจับขังในตู้พยาบาลอยู่หรือไม่
                                for fish in my_fishes:
                                    if fish.rect.collidepoint(mouse_pos) and fish.is_sick and not fish.is_dead:
                                        if quarantine_rect.colliderect(fish.rect):
                                            fish.is_sick = False
                                            fish.in_quarantine = False  # ปล่อยปลาออกจากตู้พยาบาลอัตโนมัติเมื่อหายดี
                                            item_data["qty"] -= 1
                                            break
                    else:
                        hit_fish = None
                        for fish in reversed(my_fishes):
                            if fish.rect.collidepoint(mouse_pos):
                                hit_fish = fish
                                break
                        if hit_fish:
                            dragging_fish = hit_fish
                            dragging_fish.original_pos = (hit_fish.x, hit_fish.y)
                            hit_fish.is_dragging = True
                        elif not quarantine_rect.collidepoint(mouse_pos):
                            if player_gold >= 50:
                                player_gold -= 50
                                my_fishes.append(fish())

            elif event.button == 3:
                if dragging_fish:
                    dragging_fish.x, dragging_fish.y = dragging_fish.original_pos
                    dragging_fish.is_dragging = False
                    dragging_fish = None
                slot_clicked = False
                for i, slot in enumerate(quick_slots):
                    if slot.collidepoint(mouse_pos):
                        quick_items[i] = None
                        slot_clicked = True
                if not slot_clicked: selected_slot = -1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: selected_slot = 0
            if event.key == pygame.K_2: selected_slot = 1
            if event.key == pygame.K_3: selected_slot = 2

            if event.key == pygame.K_ESCAPE:
                if is_build_mode:
                    is_build_mode = False
                    selected_decor = None
                else:
                    selected_slot = -1

            if is_build_mode and selected_decor:
                if event.key == pygame.K_q:
                    selected_decor["scale"] = max(0.1, selected_decor.get("scale", 1.0) - 0.1)
                if event.key == pygame.K_e:
                    selected_decor["scale"] = min(5.0, selected_decor.get("scale", 1.0) + 0.1)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging_fish:
                if dragging_fish.is_dead:
                    # ทิ้งถังขยะ
                    if trash_rect.collidepoint(mouse_pos):
                        dragging_fish.to_be_removed = True
                else:
                    # จับปลาหย่อนลงตู้พยาบาล
                    if quarantine_rect.collidepoint(mouse_pos):
                        dragging_fish.in_quarantine = True
                    else:
                        # ถ้าลากออกจากตู้พยาบาล ไปปล่อยในตู้ใหญ่ปกติ
                        dragging_fish.in_quarantine = False

                dragging_fish.is_dragging = False
                dragging_fish = None

    # Logic Updates
    if dragging_fish:
        dragging_fish.x, dragging_fish.y = mouse_pos[0] - (dragging_fish.size_w / 2), mouse_pos[1] - (
                    dragging_fish.size_h / 2)
        dragging_fish.rect.topleft = (dragging_fish.x, dragging_fish.y)

    for fish in my_fishes:
        fish.update_stats()
        fish.move(my_fishes)

    # ลบปลาที่ถูกทิ้งถังขยะออก
    my_fishes = [fish for fish in my_fishes if not fish.to_be_removed]

    for f in foods: f.update(my_fishes)
    foods = [f for f in foods if not f.eaten]
    for btn in top_buttons + bottom_buttons: btn.check_hover(mouse_pos)

    # --- Rendering ---
    # 1. Background
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(COLOR_DEEP_BLUE)

    # 2. Decoration Objects (Middle Layer)
    for obj in decor_objects:
        img = obj["img"]
        rect = img.get_rect(midbottom=(obj["x"], obj["y"]))
        screen.blit(img, rect)

    # 3. Fish & Food (Top Layer - but below UI)
    for f in foods: f.draw(screen)
    # Draw all fishes here to ensure they are below UI as per requirement "กันปลาว่ายทับ UI"
    for fish in my_fishes:
        fish.draw(screen)

    # 4. UI Panels (Overlay)
    top_p = pygame.Surface((SCREEN_WIDTH, 90), pygame.SRCALPHA)
    top_p.fill(COLOR_UI_BG)
    screen.blit(top_p, (0, 0))
    bot_p = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
    bot_p.fill(COLOR_UI_BG)
    screen.blit(bot_p, (0, 780))

    # วาด Quick Slots
    for i, slot in enumerate(quick_slots):
        is_sel = (i == selected_slot)
        pygame.draw.rect(screen, (40, 70, 110), slot, border_radius=12)
        pygame.draw.rect(screen, COLOR_WHITE if is_sel else (80, 80, 100), slot, width=3 if is_sel else 1,
                         border_radius=12)
        item_key = quick_items[i]
        if item_key:
            pygame.draw.circle(screen, inventory[item_key]["color"], slot.center, 22)
            font_qty = pygame.font.SysFont("Arial", 16, bold=True)
            qty_txt = font_qty.render(f"x{inventory[item_key]['qty']}", True, COLOR_WHITE)
            screen.blit(qty_txt, (slot.right - 35, slot.bottom - 22))
        screen.blit(pygame.font.SysFont("Arial", 14, bold=True).render(str(i + 1), True, (200, 200, 200)),
                    (slot.x + 8, slot.y + 5))

    screen.blit(pygame.font.SysFont("Tahoma", 28, bold=True).render(f"GOLD: {player_gold}G", True, COLOR_GOLD),
                (820, 28))
    for btn in top_buttons + bottom_buttons: btn.draw(screen)
    if medic_img: screen.blit(medic_img, quarantine_rect.topleft)

    # --- วาดถังขยะ (Trash Bin) ---
    pygame.draw.rect(screen, (80, 80, 80), trash_rect, border_radius=15)
    pygame.draw.rect(screen, (220, 50, 50), trash_rect, width=4, border_radius=15)
    trash_font = pygame.font.SysFont("Tahoma", 18, bold=True)
    screen.blit(trash_font.render("TRASH", True, COLOR_WHITE), (trash_rect.x + 18, trash_rect.y + 40))

    if selected_slot != -1 and quick_items[selected_slot]:
        active_key = quick_items[selected_slot]
        if inventory[active_key]["qty"] > 0:
            pygame.draw.circle(screen, inventory[active_key]["color"], mouse_pos, 8)
            pygame.draw.circle(screen, COLOR_WHITE, mouse_pos, 8, 2)

    # Build Mode UI
    if is_build_mode:
        decor_ui_rect = pygame.Rect(30, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 60, 100)
        pygame.draw.rect(screen, (20, 40, 70, 200), decor_ui_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_WHITE, decor_ui_rect, width=2, border_radius=15)

        for i, decor in enumerate(decor_inventory):
            decor_btn = pygame.Rect(40 + i * 110, SCREEN_HEIGHT - 210, 100, 80)
            is_sel = (selected_decor == decor)
            pygame.draw.rect(screen, (50, 100, 150) if is_sel else (30, 60, 100), decor_btn, border_radius=10)
            if is_sel:
                pygame.draw.rect(screen, COLOR_GOLD, decor_btn, width=3, border_radius=10)

            # Draw preview
            prev_img = pygame.transform.smoothscale(decor["img"], (60, 60))
            screen.blit(prev_img, (decor_btn.centerx - 30, decor_btn.centery - 35))

            name_txt = pygame.font.SysFont("Tahoma", 10).render(decor["name"], True, COLOR_WHITE)
            screen.blit(name_txt, (decor_btn.x + 5, decor_btn.bottom - 15))

        if selected_decor:
            # Draw preview at mouse
            img = selected_decor["img"]
            scale = selected_decor.get("scale", 1.0)
            w, h = img.get_size()
            scaled_img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            rect = scaled_img.get_rect(midbottom=mouse_pos)
            screen.blit(scaled_img, rect)

            # UI Hint
            hint_txt = pygame.font.SysFont("Tahoma", 16, bold=True).render("Q/E to Scale, Click to Place, ESC to Exit", True, COLOR_WHITE)
            screen.blit(hint_txt, (SCREEN_WIDTH // 2 - hint_txt.get_width() // 2, SCREEN_HEIGHT - 250))

    # Popup
    if not show_shop and not show_supplies and not dragging_fish and not is_build_mode:
        hovered_fish = None
        for fish in my_fishes:
            if fish.rect.collidepoint(mouse_pos) and not fish.is_dead:
                hovered_fish = fish
                break
        if hovered_fish:
            draw_fish_popup(screen, hovered_fish, mouse_pos)

    # Pop-ups Shop / Supplies
    if show_shop:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (25, 55, 100), shop_rect, border_radius=25)
        pygame.draw.rect(screen, COLOR_WHITE, shop_rect, width=3, border_radius=25)
        title = pygame.font.SysFont("Tahoma", 32, bold=True).render("AQUARIUM SHOP", True, COLOR_GOLD)
        screen.blit(title, (shop_rect.x + 40, shop_rect.y + 30))

        # Tabs
        tab_supplies = pygame.Rect(shop_rect.x + 30, shop_rect.y + 75, 180, 30)
        tab_decor = pygame.Rect(shop_rect.x + 220, shop_rect.y + 75, 180, 30)
        pygame.draw.rect(screen, (50, 100, 180) if shop_category == "Food & Medicine" else (30, 60, 120), tab_supplies, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(screen, (50, 100, 180) if shop_category == "Decorations" else (30, 60, 120), tab_decor, border_top_left_radius=10, border_top_right_radius=10)
        screen.blit(pygame.font.SysFont("Tahoma", 16, bold=True).render("Supplies", True, COLOR_WHITE), (tab_supplies.x + 45, tab_supplies.y + 5))
        screen.blit(pygame.font.SysFont("Tahoma", 16, bold=True).render("Decorations", True, COLOR_WHITE), (tab_decor.x + 40, tab_decor.y + 5))

        # Pagination controls
        btn_prev = pygame.Rect(shop_rect.x + 580, shop_rect.y + 30, 40, 40)
        btn_next = pygame.Rect(shop_rect.x + 630, shop_rect.y + 30, 40, 40)
        pygame.draw.rect(screen, (40, 80, 140), btn_prev, border_radius=5)
        pygame.draw.rect(screen, (40, 80, 140), btn_next, border_radius=5)
        screen.blit(pygame.font.SysFont("Tahoma", 24, bold=True).render("<", True, COLOR_WHITE), (btn_prev.x + 12, btn_prev.y + 5))
        screen.blit(pygame.font.SysFont("Tahoma", 24, bold=True).render(">", True, COLOR_WHITE), (btn_next.x + 12, btn_next.y + 5))

        current_category_items = [it for it in shop_items if (it["type"] in ["food", "medicine"] if shop_category == "Food & Medicine" else it["type"] == "decor")]
        start_idx = shop_page * 3
        display_items = current_category_items[start_idx:start_idx + 3]

        for i, item in enumerate(display_items):
            item_r = pygame.Rect(shop_rect.x + 30 + (i * 220), shop_rect.y + 110, 200, 280)
            h = item_r.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (50, 90, 150) if h else (40, 70, 120), item_r, border_radius=15)
            pygame.draw.rect(screen, COLOR_WHITE, item_r, width=2 if not h else 4, border_radius=15)

            if item["type"] == "decor":
                # Draw decoration preview from cache
                scaled_preview = get_shop_preview(item["img_path"])
                screen.blit(scaled_preview, (item_r.centerx - 40, item_r.y + 40))
            else:
                pygame.draw.circle(screen, item["color"], (item_r.centerx, item_r.y + 80), 40)

            screen.blit(pygame.font.SysFont("Tahoma", 20, bold=True).render(item["name"], True, COLOR_WHITE),
                        (item_r.x + 20, item_r.y + 140))
            p_txt = pygame.font.SysFont("Tahoma", 22, bold=True).render(f"{item['price']}G", True, COLOR_GOLD)
            screen.blit(p_txt, (item_r.centerx - p_txt.get_width() // 2, item_r.bottom - 40))

    if show_supplies:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (30, 45, 80), supplies_rect, border_radius=25)
        pygame.draw.rect(screen, COLOR_WHITE, supplies_rect, width=3, border_radius=25)
        title = pygame.font.SysFont("Tahoma", 28, bold=True).render("YOUR SUPPLIES (Click to equip)", True, COLOR_WHITE)
        screen.blit(title, (supplies_rect.x + 40, supplies_rect.y + 30))
        y_offset = 120
        for key, data in inventory.items():
            item_line = pygame.Rect(supplies_rect.x + 40, supplies_rect.y + y_offset, 620, 80)
            h = item_line.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (70, 90, 130) if h else (50, 70, 110), item_line, border_radius=10)
            pygame.draw.circle(screen, data["color"], (item_line.x + 50, item_line.centery), 25)
            screen.blit(pygame.font.SysFont("Tahoma", 24, bold=True).render(data["name"], True, COLOR_WHITE),
                        (item_line.x + 100, item_line.centery - 15))
            screen.blit(pygame.font.SysFont("Tahoma", 24).render(f"{data['qty']} units", True, COLOR_GOLD),
                        (item_line.right - 180, item_line.centery - 15))
            y_offset += 100

    pygame.display.flip()
    clock.tick(60)

pygame.quit()