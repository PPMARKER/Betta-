import pygame
import cv2
import numpy as np
import os
from scipy.ndimage import gaussian_filter
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class LightManager:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        # Use a lower resolution for the filter generation to ensure performance
        # especially since we are using scipy's gaussian_filter
        self.gen_scale = 0.5
        self.gw = int(self.width * self.gen_scale)
        self.gh = int(self.height * self.gen_scale)

        self.mask = self._create_mask()
        self.time = 0
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Pre-calculate angles and distance from top-right source on the smaller grid
        src_x, src_y = self.gw * 1.1, -self.gh * 0.1

        Y, X = np.indices((self.gh, self.gw))
        dx = X - src_x
        dy = Y - src_y

        self.angles = np.arctan2(dy, dx)
        dist = np.sqrt(dx**2 + dy**2)

        # Distance fade: stronger near top-right
        self.fade = np.clip(1.2 - dist / (self.gw * 1.3), 0, 1)

        # Warm Orange Color
        self.color_rgb = np.array([255, 180, 80], dtype=np.uint8)

    def _create_mask(self):
        """Detect the water area in Tank.png using OpenCV."""
        path = os.path.join("asset", "Tank", "Tank.png")
        mask = None
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                # Mask transparent areas (water)
                mask = (img[:, :, 3] < 128).astype(np.uint8) * 255
                # Resize to generation resolution
                mask = cv2.resize(mask, (self.gw, self.gh), interpolation=cv2.INTER_NEAREST)

                # Clean up and fill holes
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    c = max(contours, key=cv2.contourArea)
                    mask = np.zeros_like(mask)
                    cv2.drawContours(mask, [c], -1, 255, -1)

        if mask is None:
            mask = np.zeros((self.gh, self.gw), dtype=np.uint8)
            cv2.rectangle(mask, (0, int(self.gh*0.1)), (self.gw, int(self.gh*0.85)), 255, -1)

        return mask

    def update(self):
        """Update the animation using NumPy and SciPy."""
        self.time += 0.05

        # Create shimmering rays
        ray_map = np.sin(self.angles * 10 + self.time * 0.7) * 0.4 + \
                  np.sin(self.angles * 18 - self.time * 1.1) * 0.3 + \
                  np.sin(self.angles * 35 + self.time * 2.2) * 0.3

        ray_map = (ray_map + 1.0) / 2.0
        ray_map = np.power(ray_map, 1.5)

        # Apply distance fade and limit intensity
        alpha_map = (ray_map * self.fade * 210).astype(np.float32)

        # Use SciPy for smooth blur
        alpha_map = gaussian_filter(alpha_map, sigma=2.0)
        alpha_map = alpha_map.astype(np.uint8)

        # Apply the tank mask
        alpha_map = cv2.bitwise_and(alpha_map, alpha_map, mask=self.mask)

        # Construct RGBA image at generation resolution
        res = np.zeros((self.gh, self.gw, 4), dtype=np.uint8)
        res[:, :, 0] = self.color_rgb[0]
        res[:, :, 1] = self.color_rgb[1]
        res[:, :, 2] = self.color_rgb[2]
        res[:, :, 3] = alpha_map

        # Upscale to full resolution for Pygame
        res_full = cv2.resize(res, (self.width, self.height), interpolation=cv2.INTER_LINEAR)

        # Convert to Pygame Surface
        self.surface = pygame.image.frombuffer(res_full.tobytes(), (self.width, self.height), "RGBA")

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))
