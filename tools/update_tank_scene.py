import re

with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

# 1. Update __init__
if 'self.light_manager = LightManager()' not in content:
    content = content.replace(
        'self.ui_manager = UIManager(on_decor_pickup=self.on_decor_pickup)',
        'self.ui_manager = UIManager(on_decor_pickup=self.on_decor_pickup)\n        self.light_manager = LightManager()'
    )

# 2. Update update()
if 'self.light_manager.update()' not in content:
    content = content.replace(
        'self.ui_manager.update()',
        'self.ui_manager.update()\n        self.light_manager.update()'
    )

# 3. Update draw()
# We want it after decorations but before food/fish
if 'self.light_manager.draw(surface)' not in content:
    content = content.replace(
        'for f in self.foods: f.draw(surface)',
        'self.light_manager.draw(surface)\n        for f in self.foods: f.draw(surface)'
    )

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)
