with open('managers/tank_scene.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "        def go_breeding(self):" in line:
        new_lines.append("    def go_breeding(self):\n")
        continue
    if "        from managers.breeding_scene import BreedingScene" in line and "    def go_breeding" in new_lines[-1]:
        new_lines.append("        from managers.breeding_scene import BreedingScene\n")
        continue
    if "        if hasattr(self, 'sm') and self.sm:" in line and "    def go_breeding" in "".join(new_lines[-5:]):
        new_lines.append("        if hasattr(self, 'sm') and self.sm:\n")
        continue
    if "            if isinstance(self, BreedingScene):" in line:
        new_lines.append("            if isinstance(self, BreedingScene):\n")
        continue
    if "                self.sm.change_scene(self.sm.tank_scene)" in line:
        new_lines.append("                self.sm.change_scene(self.sm.tank_scene)\n")
        continue
    if "            else:" in line:
        new_lines.append("            else:\n")
        continue
    if "                self.sm.change_scene(self.sm.breeding_scene)" in line:
        new_lines.append("                self.sm.change_scene(self.sm.breeding_scene)\n")
        continue
    new_lines.append(line)

with open('managers/tank_scene.py', 'w') as f:
    f.writelines(new_lines)
