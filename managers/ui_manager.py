from ui.hud import HUD; from ui.shop_panel import ShopPanel; from ui.inventory_panel import InventoryPanel
class UIManager:
    def __init__(self, on_decor_pickup=None):
        self.hud, self.shop, self.inventory = HUD(), ShopPanel(), InventoryPanel(on_decor_pickup=on_decor_pickup)
        self.components = [self.hud, self.shop, self.inventory]
    def handle_event(self, event):
        for c in reversed(self.components):
            if c.visible and c.handle_event(event): return True
        for c in reversed(self.components):
            if not c.visible and c.handle_event(event): return True
        return False
    def update(self):
        for c in self.components: c.update()
    def draw(self, surface):
        for c in self.components: c.draw(surface)
    def show_shop(self): self.shop.visible, self.inventory.visible = True, False
    def show_inventory(self): self.inventory.visible, self.shop.visible = True, False
