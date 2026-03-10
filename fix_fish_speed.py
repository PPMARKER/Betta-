with open('entities/fish.py', 'r') as f:
    content = f.read()

# 1. Expand recovery time from 10 to 40 seconds
content = content.replace(
    'if now - self.treatment_timer > 10:',
    'if now - self.treatment_timer > 40:'
)

# 2. Reduce swim speed by 0.5 when not chasing food
# In move(): cur_speed = self.max_speed
content = content.replace(
    't_angle, cur_speed, ax, ay = self.angle, self.max_speed, 0, 0',
    't_angle, cur_speed, ax, ay = self.angle, self.max_speed - 0.5, 0, 0'
)

with open('entities/fish.py', 'w') as f:
    f.write(content)
