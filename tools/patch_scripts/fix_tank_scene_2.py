import os

def fix():
    with open('managers/tank_scene.py', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Fix indentation of go_breeding
        if "if hasattr(self, 'sm') and self.sm:" in line and "    def go_breeding" in lines[lines.index(line)-3]:
             new_lines.append("        if hasattr(self, 'sm') and self.sm:\n")
             continue
        if "self.sm.change_scene(self.sm.breeding_scene)" in line:
             new_lines.append("            self.sm.change_scene(self.sm.breeding_scene)\n")
             continue

        # Fix handle_event first line
        if "if self.ui_manager.handle_event(e): return" in line:
             new_lines.append("        if self.ui_manager.handle_event(e): return\n")
             continue

        new_lines.append(line)

    with open('managers/tank_scene.py', 'w') as f:
        f.writelines(new_lines)

fix()
