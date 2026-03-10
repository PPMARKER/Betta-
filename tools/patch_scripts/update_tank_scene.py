import re

with open('managers/tank_scene.py', 'r') as f:
    content = f.read()

# 1. Update initialization
content = content.replace(
    'self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor = [Fish(), Fish()], [], [], None, None',
    'self.fishes, self.foods, self.decor_objects, self.dragging_fish, self.dragging_decor = [Fish(gender="Male"), Fish(gender="Female")], [], [], None, None'
)

# 2. Remove quarantine_rect from init and handle_event
content = content.replace(
    'self.trash_rect, self.quarantine_rect = pygame.Rect(*TRASH_RECT_COORDS), pygame.Rect(*QUARANTINE_RECT_COORDS)',
    'self.trash_rect = pygame.Rect(*TRASH_RECT_COORDS)'
)

# 3. Update medicine logic
med_logic_old = """                        elif it == "med":
                            for f in self.fishes:
                                if f.rect.collidepoint(mp) and f.is_sick and not f.is_dead and self.quarantine_rect.colliderect(f.rect): f.is_sick, f.in_quarantine, d["qty"] = False, False, d["qty"] - 1; break"""

med_logic_new = """                        elif it == "med":
                            treated = False
                            for f in self.fishes:
                                if f.is_sick and not f.is_dead and not f.is_treated:
                                    f.is_treated = True
                                    f.treatment_timer = time.time()
                                    treated = True
                            if treated:
                                d["qty"] -= 1
                                # TODO: Start drop effect at mp"""

content = content.replace(med_logic_old, med_logic_new)

# 4. Update mouseup for dragging fish
content = content.replace(
    'else: self.dragging_fish.in_quarantine = self.quarantine_rect.collidepoint(mp)',
    'pass'
)

# 5. Remove medic tank blit
content = re.sub(r'med = assets\.load_image\(os\.path\.join\("asset", "Ui", "medic_tank\.png"\), scale=\(300, 180\)\)\s+if med: self\.ui_surf\.blit\(med, self\.quarantine_rect\.topleft\)', '', content)

# 6. Update fish popups
content = content.replace(
    'surface.blit(fs.render(f"Age: {h.age} Days", True, COLOR_WHITE), (pr.x+12, pr.y+12))',
    'surface.blit(fs.render(f"Age: {h.age} Days ({h.gender})", True, COLOR_WHITE), (pr.x+12, pr.y+12))'
)

old_status = """            sc = (255, 50, 50) if h.is_sick else (50, 255, 50)
            st = fs.render("HEALTH: ", True, COLOR_WHITE)
            surface.blit(st, (pr.x+12, pr.y+36))
            surface.blit(fs.render("SICK" if h.is_sick else "HEALTHY", True, sc), (pr.x+12+st.get_width(), pr.y+36))"""

new_status = """            sc = (255, 50, 50) if h.is_sick else (50, 255, 50)
            status_text = "SICK" if h.is_sick else "HEALTHY"
            if h.is_treated: status_text = "RECOVERING"
            st = fs.render("HEALTH: ", True, COLOR_WHITE)
            surface.blit(st, (pr.x+12, pr.y+36))
            surface.blit(fs.render(status_text, True, sc), (pr.x+12+st.get_width(), pr.y+36))"""

content = content.replace(old_status, new_status)

with open('managers/tank_scene.py', 'w') as f:
    f.write(content)
