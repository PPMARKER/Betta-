from core.theme import COLOR_FOOD_PELLETS, COLOR_FOOD_MOINA, COLOR_MEDICINE
SHOP_ITEMS = [
    {"name": "Pellets", "price": 50, "qty": 30, "color": COLOR_FOOD_PELLETS, "type": "food", "id": "food_p"},
    {"name": "Moina", "price": 100, "qty": 20, "color": COLOR_FOOD_MOINA, "type": "food", "id": "food_m"},
    {"name": "Medicine", "price": 100, "qty": 10, "color": COLOR_MEDICINE, "type": "medicine", "id": "med"},
    {"name": "Build 1", "price": 200, "type": "decor", "img_path": "asset/build/Build_1.png"},
    {"name": "Build 2", "price": 250, "type": "decor", "img_path": "asset/build/Build_2.png"},
    {"name": "Build 3", "price": 300, "type": "decor", "img_path": "asset/build/Build_3.png"},
    {"name": "Build 4", "price": 350, "type": "decor", "img_path": "asset/build/Build_4.png"},
    {"name": "Build 5", "price": 400, "type": "decor", "img_path": "asset/build/Build_5.png"},
    {"name": "Build 6", "price": 450, "type": "decor", "img_path": "asset/build/Build_6.png"},
    {"name": "Build 7", "price": 500, "type": "decor", "img_path": "asset/build/Build_7.png"},
    {"name": "Build 8", "price": 550, "type": "decor", "img_path": "asset/build/Build_8.png"},
]
INITIAL_INVENTORY = {
    "food_p": {"name": "Pellets", "color": COLOR_FOOD_PELLETS, "qty": 10, "type": "food"},
    "food_m": {"name": "Moina", "color": COLOR_FOOD_MOINA, "qty": 5, "type": "food"},
    "med": {"name": "Medicine", "color": COLOR_MEDICINE, "qty": 2, "type": "medicine"}
}
QUICK_ITEMS_DEFAULT = ["food_p", "food_m", "med"]
