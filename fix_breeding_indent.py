with open('managers/breeding_scene.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "        def __init__" in line:
        new_lines.append("    def __init__(self, scene_manager=None):\n")
        continue
    if "        super().__init__" in line:
        new_lines.append("        super().__init__(scene_manager)\n")
        continue
    if "        self.btn_tank_switch" in line:
        new_lines.append("        " + line.strip() + "\n")
        continue
    if "        self.fishes = []" in line:
        new_lines.append("        self.fishes = []\n")
        continue
    if "        self.eggs = []" in line:
        new_lines.append("        self.eggs = []\n")
        continue
    if "        self.breeding_start_time" in line:
        new_lines.append("        self.breeding_start_time = 0\n")
        continue
    if "        self.breeding_in_progress" in line:
        new_lines.append("        self.breeding_in_progress = False\n")
        continue
    if "        self.eggs_spawned" in line:
        new_lines.append("        self.eggs_spawned = False\n")
        continue
    new_lines.append(line)

with open('managers/breeding_scene.py', 'w') as f:
    f.writelines(new_lines)
