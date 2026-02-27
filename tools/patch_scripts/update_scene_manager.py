with open('managers/scene_manager.py', 'r') as f:
    content = f.read()

if 'self.tank_scene = None' not in content:
    content = content.replace(
        'def __init__(self): self.current_scene = None',
        'def __init__(self): self.current_scene = None; self.tank_scene = None; self.breeding_scene = None'
    )

with open('managers/scene_manager.py', 'w') as f:
    f.write(content)
