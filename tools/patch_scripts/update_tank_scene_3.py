import re

with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

# Update Breed button callback
content = re.sub(
    r'self\.ui_manager\.hud\.add_button\(1310, 20, 110, 45, "Breed", lambda: None, \'top\'\)',
    'self.ui_manager.hud.add_button(1310, 20, 110, 45, "Breed", self.go_breeding, \'top\')',
    content
)

# Add go_breeding method and dragging into breeding area logic
if 'def go_breeding' not in content:
    insertion_point = content.find('    def on_decor_pickup')
    method = """    def go_breeding(self):
        # We need a reference to scene_manager.
        # In main.py, sm.tank_scene = TankScene(), but TankScene doesn't have sm reference yet.
        # Let's assume we can get it from somewhere or pass it.
        # Quick fix: find the sm in main's scope or similar.
        # Better: pass sm to TankScene.__init__
        if hasattr(self, 'sm') and self.sm:
            self.sm.change_scene(self.sm.breeding_scene)

"""
    content = content[:insertion_point] + method + content[insertion_point:]

# Update mouseup for breeding area
breeding_logic = """        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.dragging_fish:
            if self.dragging_fish.is_dead:
                if self.trash_rect.collidepoint(mp): self.dragging_fish.to_be_removed = True
            elif mp[0] > SCREEN_WIDTH - 200 and mp[1] < 100: # Area near Breed button
                # Transfer fish to breeding scene
                if hasattr(self, 'sm') and self.sm:
                    self.dragging_fish.is_dragging = False
                    self.dragging_fish.in_breeding_mode = True
                    self.sm.breeding_scene.fishes.append(self.dragging_fish)
                    self.fishes.remove(self.dragging_fish)
                    self.dragging_fish = None
                    return
            self.dragging_fish.is_dragging, self.dragging_fish = False, None"""

content = re.sub(r'elif e\.type == pygame\.MOUSEBUTTONUP and e\.button == 1 and self\.dragging_fish:.*?self\.dragging_fish = False, None', breeding_logic, content, flags=re.DOTALL)

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)
