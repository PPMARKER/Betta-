import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from managers.scene_manager import SceneManager; from managers.tank_scene import TankScene; from managers.breeding_scene import BreedingScene
def main():
    pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption("Ocean Tycoon - Refactored"); clock = pygame.time.Clock()
    sm = SceneManager()
    sm.tank_scene = TankScene(sm)
    sm.breeding_scene = BreedingScene(sm)
    sm.change_scene(sm.tank_scene)
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            sm.handle_event(e)
        sm.update(); sm.draw(screen); pygame.display.flip(); clock.tick(FPS)
    pygame.quit()
if __name__ == "__main__": main()
