import re

with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

# 1. Add import
if 'from entities.medicine_drop import MedicineDrop' not in content:
    content = content.replace(
        'from entities.fish import Fish; from entities.food import Food; from entities.decoration import Decoration; from managers.light_manager import LightManager',
        'from entities.fish import Fish; from entities.food import Food; from entities.decoration import Decoration; from managers.light_manager import LightManager; from entities.medicine_drop import MedicineDrop'
    )

# 2. Add self.med_drops to init
if 'self.med_drops = []' not in content:
    content = content.replace(
        'self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor = [Fish(gender="Male"), Fish(gender="Female")], [], [], None, None',
        'self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor, self.med_drops = [Fish(gender="Male"), Fish(gender="Female")], [], [], None, None, []'
    )

# 3. Update medicine logic to add effect
med_effect_logic = """                                # TODO: Start drop effect at mp
                                self.med_drops.append(MedicineDrop(mp[0], mp[1]))"""
content = content.replace('# TODO: Start drop effect at mp', 'self.med_drops.append(MedicineDrop(mp[0], mp[1]))')

# 4. Update and Draw med_drops
update_med = """        for m in self.med_drops: m.update()
        self.med_drops = [m for m in self.med_drops if not m.done]
        self.ui_manager.update()"""
content = content.replace('self.ui_manager.update()', update_med)

draw_med = """        # 4. Fishes
        for f in self.fishes: f.draw(None)

        # 4.5 Medicine Drops
        for m in self.med_drops: m.draw(self.ui_surf)"""
content = content.replace('        # 4. Fishes\n        for f in self.fishes: f.draw(None)', draw_med)

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)
