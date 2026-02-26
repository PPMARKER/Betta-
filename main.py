import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
# Import gl_manager first to ensure the module is loaded
import managers.gl_manager

def main():
    pygame.init()
    # Use OpenGL
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Ocean Tycoon - Refactored")
    clock = pygame.time.Clock()

    # Initialize GLManager
    managers.gl_manager.init_gl()

    # Now import scenes after GL is initialized
    from managers.scene_manager import SceneManager
    from managers.tank_scene import TankScene

    sm = SceneManager()
    sm.change_scene(TankScene())
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            sm.handle_event(e)
        sm.update()

        # Clear screen via GL
        managers.gl_manager.gl_manager.clear((0.05, 0.1, 0.2, 1.0))

        # Draw scene
        sm.draw(None)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
