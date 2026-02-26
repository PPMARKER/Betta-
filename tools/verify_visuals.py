import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import cv2
import numpy as np
from managers.light_manager import LightManager
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
lm = LightManager()

# Update a few times to get some animation state
for _ in range(20):
    lm.update()

screen.fill((50, 50, 100)) # Fake water background
lm.draw(screen)

# Save the result
pygame.image.save(screen, "verify_light.png")

# Check if alpha is around 115 (45%)
# The light manager creates a surface with alpha.
# When we draw it onto a surface, it blends.
# Let's inspect the light manager's internal surface alpha.
alpha_channel = pygame.surfarray.array_alpha(lm.surface)
max_alpha = np.max(alpha_channel)
print(f"Max alpha detected: {max_alpha} ({max_alpha/255:.1%})")

if 110 <= max_alpha <= 120:
    print("Intensity is correct (~45%)")
else:
    print(f"Intensity might be off: {max_alpha}")

pygame.quit()
