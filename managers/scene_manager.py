class Scene:
    def handle_event(self, event): pass
    def update(self): pass
    def draw(self, surface): pass
class SceneManager:
    def __init__(self): self.current_scene = None; self.tank_scene = None; self.breeding_scene = None
    def change_scene(self, s): self.current_scene = s
    def handle_event(self, e):
        if self.current_scene: self.current_scene.handle_event(e)
    def update(self):
        if self.current_scene: self.current_scene.update()
    def draw(self, s):
        if self.current_scene: self.current_scene.draw(s)
