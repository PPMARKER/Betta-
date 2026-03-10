import re

with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

# Add navigation logic
nav_logic = """
    def __init__(self, scene_manager=None):
        self.sm = scene_manager
        self.ui_manager = UIManager(on_decor_pickup=self.on_decor_pickup)
        self.light_manager = LightManager()
        self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor, self.med_drops = [Fish(gender="Male"), Fish(gender="Female")], [], [], None, None, []
        self.trash_rect = pygame.Rect(*TRASH_RECT_COORDS)

        # UI Buttons
        self.ui_manager.hud.add_button(150, 820, 120, 50, "SHOP", self.ui_manager.show_shop)
        self.ui_manager.hud.add_button(280, 820, 120, 50, "INVENTORY", self.ui_manager.show_inventory)
        self.ui_manager.hud.add_button(410, 820, 120, 50, "SPECIES", lambda: None)
        self.ui_manager.hud.add_button(20, 820, 120, 50, "MENU", lambda: None)

        self.btn_more = self.ui_manager.hud.add_button(1050, 20, 120, 45, "More Tank", self.toggle_more, 'top')
        self.btn_sell = self.ui_manager.hud.add_button(1180, 20, 120, 45, "Sell Tank", lambda: None, 'top')
        self.btn_breed_nav = self.ui_manager.hud.add_button(1310, 20, 110, 45, "Breed", self.go_breeding, 'top')

        # Extra buttons (initially hidden)
        self.btn_tank_switch = self.ui_manager.hud.add_button(1050, 75, 120, 45, "Breeding", self.go_breeding, 'top')
        self.btn_tank_switch.visible = False

        self.ui_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def toggle_more(self):
        self.btn_tank_switch.visible = not self.btn_tank_switch.visible
        # Set text based on context
        from managers.breeding_scene import BreedingScene
        if isinstance(self, BreedingScene):
            self.btn_tank_switch.text = "Tank 1"
        else:
            self.btn_tank_switch.text = "Breeding"
"""

# Replace existing __init__ and go_breeding with new structure
pattern = r'def __init__\(self, scene_manager=None\):.*?self\.ui_surf = pygame\.Surface\(.*?SRCALPHA\)'
content = re.sub(pattern, nav_logic, content, flags=re.DOTALL)

# Fix go_breeding in TankScene to handle switching back
go_breed_logic = """    def go_breeding(self):
        from managers.breeding_scene import BreedingScene
        if hasattr(self, 'sm') and self.sm:
            if isinstance(self, BreedingScene):
                self.sm.change_scene(self.sm.tank_scene)
            else:
                self.sm.change_scene(self.sm.breeding_scene)
"""
content = re.sub(r'def go_breeding\(self\):.*?self\.sm\.change_scene\(self\.sm\.breeding_scene\)', go_breed_logic, content, flags=re.DOTALL)

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)

# Update BreedingScene to adjust the button text in its own init if needed
with open('managers/breeding_scene.py', 'r') as f:
    b_content = f.read()

b_init = """    def __init__(self, scene_manager=None):
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
"""
b_content = re.sub(r'def __init__\(self, scene_manager=None\):.*?self\.fishes = \[\]', b_init, b_content, flags=re.DOTALL)

with open('managers/breeding_scene.py', 'w') as f:
    f.write(b_content)
