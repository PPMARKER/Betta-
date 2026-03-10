import re

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from managers.scene_manager import SceneManager; from managers.tank_scene import TankScene',
    'from managers.scene_manager import SceneManager; from managers.tank_scene import TankScene; from managers.breeding_scene import BreedingScene'
)

old_init = """    sm = SceneManager(); sm.change_scene(TankScene())"""
new_init = """    sm = SceneManager()
    sm.tank_scene = TankScene()
    sm.breeding_scene = BreedingScene(sm)
    sm.change_scene(sm.tank_scene)"""

content = content.replace(old_init, new_init)

with open('main.py', 'w') as f:
    f.write(content)
