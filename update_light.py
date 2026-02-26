import sys

with open('managers/light_manager.py', 'r') as f:
    content = f.read()

content = content.replace('alpha_map = (ray_map * self.fade * 90).astype(np.float32)',
                          'alpha_map = (ray_map * self.fade * 115).astype(np.float32)')

with open('managers/light_manager.py', 'w') as f:
    f.write(content)
