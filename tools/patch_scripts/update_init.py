with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

content = content.replace('def __init__(self):', 'def __init__(self, scene_manager=None):\n        self.sm = scene_manager')

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace('sm.tank_scene = TankScene()', 'sm.tank_scene = TankScene(sm)')
with open('main.py', 'w') as f:
    f.write(content)
