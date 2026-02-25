from data.items import INITIAL_INVENTORY, QUICK_ITEMS_DEFAULT
class EventDispatcher:
    def __init__(self): self.listeners = {}
    def subscribe(self, event_type, callback):
        if event_type not in self.listeners: self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    def emit(self, event_type, *args, **kwargs):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]: callback(*args, **kwargs)
class GameState:
    def __init__(self):
        self.gold = 1000
        self.inventory = {k: v.copy() for k, v in INITIAL_INVENTORY.items()}
        self.quick_items = list(QUICK_ITEMS_DEFAULT)
        self.decor_inventory = []
        self.selected_slot = -1
        self.events = EventDispatcher()
    def add_gold(self, amount):
        self.gold += amount
        self.events.emit("gold_changed", self.gold)
    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            self.events.emit("gold_changed", self.gold)
            return True
        return False
    def add_to_inventory(self, item_id, qty):
        if item_id in self.inventory: self.inventory[item_id]["qty"] += qty
        self.events.emit("inventory_changed")
    def add_decor(self, decor_data):
        self.decor_inventory.append(decor_data)
        self.events.emit("inventory_changed")
game_state = GameState()
