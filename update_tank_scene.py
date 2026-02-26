import sys

with open('managers/tank_scene.py', 'r') as f:
    lines = f.readlines()

new_lines = []
light_draw_line = ""
for line in lines:
    if "self.light_manager.draw(surface)" in line:
        light_draw_line = line
        continue
    if "self.ui_manager.draw(surface)" in line:
        new_lines.append(light_draw_line)
    new_lines.append(line)

with open('managers/tank_scene.py', 'w') as f:
    f.writelines(new_lines)
