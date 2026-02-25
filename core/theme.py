import pygame
COLOR_DEEP_BLUE = (10, 35, 66)
COLOR_OCEAN_BLUE = (30, 144, 255)
COLOR_SAND = (244, 164, 96)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_UI_BG = (20, 50, 90, 220)
COLOR_BTN_NORMAL = (40, 90, 150)
COLOR_BTN_HOVER = (60, 120, 200)
COLOR_FOOD_PELLETS = (139, 69, 19)
COLOR_FOOD_MOINA = (255, 50, 50)
COLOR_MEDICINE = (50, 255, 50)
FISH_COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255), (100, 255, 255), (255, 165, 0), (160, 32, 240), (240, 230, 140), (0, 255, 127)]
_fonts = {}
def get_font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]
