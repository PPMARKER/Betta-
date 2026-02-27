with open('managers/tank_scene.py', 'r') as f:
    lines = f.readlines()

# Line 71-72 area has issues
# 71	                game_state.selected_slot = -1
# 72	                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.dragging_fish:

# It should be:
#             elif e.button == 3:
#                 if self.dragging_fish: ...
#                 game_state.selected_slot = -1
#         elif e.type == pygame.MOUSEBUTTONUP ...

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "elif e.type == pygame.MOUSEBUTTONUP" in line:
        # Check if it's wrongly indented inside MOUSEBUTTONDOWN
        # It should be at the same level as "if e.type == pygame.MOUSEBUTTONDOWN:"
        new_lines.append("        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.dragging_fish:\n")
        continue
    if "if self.dragging_fish.is_dead:" in line and "            if self.dragging_fish.is_dead:" not in line:
         new_lines.append("            " + line.lstrip())
         continue
    if "if self.trash_rect.collidepoint(mp):" in line and "                if self.trash_rect.collidepoint(mp):" not in line:
         new_lines.append("                " + line.lstrip())
         continue
    if "elif mp[0] > SCREEN_WIDTH - 200" in line:
         new_lines.append("            " + line.lstrip())
         continue
    if "# Transfer fish" in line:
         new_lines.append("                " + line.lstrip())
         continue
    if "if hasattr(self, 'sm')" in line and "                if hasattr(self, 'sm')" not in line:
         new_lines.append("                " + line.lstrip())
         continue
    if "self.dragging_fish.is_dragging = False" in line and "                    self.dragging_fish.is_dragging = False" not in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "self.dragging_fish.in_breeding_mode = True" in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "self.sm.breeding_scene.fishes.append" in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "self.fishes.remove" in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "self.dragging_fish = None" in line and "                    self.dragging_fish = None" not in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "return" in line and "                    return" not in line:
         new_lines.append("                    " + line.lstrip())
         continue
    if "self.dragging_fish.is_dragging, self.dragging_fish = False, None" in line:
         new_lines.append("            self.dragging_fish.is_dragging, self.dragging_fish = False, None\n")
         continue

    new_lines.append(line)

with open('managers/tank_scene.py', 'w') as f:
    f.writelines(new_lines)
