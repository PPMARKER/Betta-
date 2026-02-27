with open('entities/fish.py', 'r') as f:
    content = f.read()

# Update draw to respect size
content = content.replace(
    'gl_mod.gl_manager.draw_fish(orig, self.x, self.y, self.size_w, self.size_h, color=tuple(color_mult), angle=angle, flip_x=flip_x, speed=speed)',
    'gl_mod.gl_manager.draw_fish(orig, self.x, self.y, self.size_w, self.size_h, color=tuple(color_mult), angle=angle, flip_x=flip_x, speed=speed)'
)
# It already uses size_w and size_h.

# Make sure baby fish grow
# Current update_stats:
# if self.age < 15:
#     self.age += 1
#     self.growth_scale = min(1.2, 0.6 + (self.age * 0.04))
#     self.update_size()

# Let's change starting growth_scale for babies
# Baby fish starting at age 0 with growth_scale 0.2
# Then it should grow up to 0.6 and then more.

content = content.replace(
    'self.growth_scale = min(1.2, 0.6 + (self.age * 0.04))',
    'self.growth_scale = min(1.2, 0.2 + (self.age * 0.08))'
)

with open('entities/fish.py', 'w') as f:
    f.write(content)
