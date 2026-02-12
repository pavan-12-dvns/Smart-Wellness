# database.py

# Macros per 100g: cal, protein (pro), carbs (carb), fat, fiber (fib)
FOOD_DB = {
    # --- Protein Rich ---
    "Chicken Breast": {"cal": 165, "pro": 31, "carb": 0, "fat": 3.6, "fib": 0},
    "Egg": {"cal": 155, "pro": 13, "carb": 1.1, "fat": 11, "fib": 0},
    "Paneer": {"cal": 265, "pro": 18, "carb": 6, "fat": 20, "fib": 0},
    "Fish (Tilapia)": {"cal": 128, "pro": 26, "carb": 0, "fat": 2.7, "fib": 0},
    "Greek Yogurt": {"cal": 59, "pro": 10, "carb": 3.6, "fat": 0.4, "fib": 0},
    "Soya Chunks": {"cal": 345, "pro": 52, "carb": 33, "fat": 0.5, "fib": 13},
    "Milk": {"cal": 62, "pro": 3.2, "carb": 4.8, "fat": 3.3, "fib": 0},
    "Curd (Dahi)": {"cal": 61, "pro": 3.5, "carb": 4.7, "fat": 3.3, "fib": 0},
    "Whey Protein": {"cal": 390, "pro": 80, "carb": 5, "fat": 4, "fib": 0},

    # --- Carb Rich ---
    "Rice": {"cal": 130, "pro": 2.7, "carb": 28, "fat": 0.3, "fib": 0.4},
    "Oats": {"cal": 389, "pro": 17, "carb": 66, "fat": 7, "fib": 10},
    "Banana": {"cal": 89, "pro": 1.1, "carb": 23, "fat": 0.3, "fib": 2.6},
    "Sweet Potato": {"cal": 86, "pro": 1.6, "carb": 20, "fat": 0.1, "fib": 3},
    "Whole Wheat Bread": {"cal": 247, "pro": 13, "carb": 41, "fat": 3.4, "fib": 7},
    "Roti (Chapati)": {"cal": 297, "pro": 10, "carb": 45, "fat": 7, "fib": 9},
    "Potato": {"cal": 77, "pro": 2, "carb": 17, "fat": 0.1, "fib": 2.2},

    # --- Fat Rich ---
    "Almonds": {"cal": 579, "pro": 21, "carb": 22, "fat": 50, "fib": 12},
    "Peanut Butter": {"cal": 588, "pro": 25, "carb": 20, "fat": 50, "fib": 6},
    "Avocado": {"cal": 160, "pro": 2, "carb": 8.5, "fat": 15, "fib": 6.7},
    "Walnuts": {"cal": 654, "pro": 15, "carb": 14, "fat": 65, "fib": 6.7},
    "Olive Oil": {"cal": 884, "pro": 0, "carb": 0, "fat": 100, "fib": 0},
    "Peanuts": {"cal": 567, "pro": 26, "carb": 16, "fat": 49, "fib": 9},

    # --- Fiber Rich ---
    "Dal (Lentils)": {"cal": 116, "pro": 9, "carb": 20, "fat": 0.4, "fib": 8},
    "Broccoli": {"cal": 34, "pro": 2.8, "carb": 6.6, "fat": 0.4, "fib": 2.6},
    "Chia Seeds": {"cal": 486, "pro": 17, "carb": 42, "fat": 31, "fib": 34},
    "Chickpeas": {"cal": 164, "pro": 9, "carb": 27, "fat": 2.6, "fib": 7.6},
    "Apples": {"cal": 52, "pro": 0.3, "carb": 14, "fat": 0.2, "fib": 2.4},
    "Spinach": {"cal": 23, "pro": 2.9, "carb": 3.6, "fat": 0.4, "fib": 2.2},
    "Carrot": {"cal": 41, "pro": 0.9, "carb": 10, "fat": 0.2, "fib": 2.8},
    "Cucumber": {"cal": 15, "pro": 0.7, "carb": 3.6, "fat": 0.1, "fib": 0.5},

# ... your other foods ...
    "Orange Juice": {"cal": 45, "pro": 0.7, "carb": 10, "fat": 0.2, "fib": 0.2},
    "Apple Juice": {"cal": 46, "pro": 0.1, "carb": 11, "fat": 0.1, "fib": 0.2},
    "Sugarcane Juice": {"cal": 270, "pro": 0, "carb": 73, "fat": 0, "fib": 0}

}

MACRO_SOURCES = {
    "Protein": ["Chicken Breast", "Soya Chunks", "Egg", "Paneer", "Milk", "Curd (Dahi)", "Whey Protein"],
    "Carbs": ["Rice", "Sweet Potato", "Whole Wheat Bread", "Oats", "Roti (Chapati)", "Potato", "Banana"],
    "Fats": ["Almonds", "Avocado", "Peanut Butter", "Walnuts", "Peanuts"],
    "Fiber": ["Chia Seeds", "Chickpeas", "Broccoli", "Dal (Lentils)", "Spinach", "Carrot", "Apples"]
}



