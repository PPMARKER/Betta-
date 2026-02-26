import sys

with open('managers/tank_scene.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'bg = assets.load_image(os.path.join("asset", "Tank", "Tank.png"), alpha=False)' in line:
        new_lines.append('        surface.fill(COLOR_OCEAN_BLUE)\n')
        new_lines.append('        bg = assets.load_image(os.path.join("asset", "Tank", "Tank.png"), alpha=True)\n')
    elif 'if bg: surface.blit(bg, (0,0))' in line:
        new_lines.append('        if bg: surface.blit(bg, (0,0))\n')
    elif 'else: surface.fill(COLOR_DEEP_BLUE)' in line:
        continue # Skip the else fill
    else:
        new_lines.append(line)

with open('managers/tank_scene.py', 'w') as f:
    f.writelines(new_lines)
