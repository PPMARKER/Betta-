with open('ui/hud.py', 'r') as f:
    content = f.read()

# Make sure HUD.draw exists and blits the UI images
if "def draw(self, surface):" not in content:
    draw_method = """    def draw(self, surface):
        from managers.asset_manager import assets
        import os
        top_img = assets.load_image(os.path.join("asset", "Ui", "top_Ui.png"), scale=(SCREEN_WIDTH, 90))
        bot_img = assets.load_image(os.path.join("asset", "Ui", "bottom_ui.png"), scale=(SCREEN_WIDTH, 120))
        if top_img: surface.blit(top_img, (0, 0))
        if bot_img: surface.blit(bot_img, (0, 780))
        super().draw(surface)"""
    content += "\n" + draw_method

with open('ui/hud.py', 'w') as f:
    f.write(content)
