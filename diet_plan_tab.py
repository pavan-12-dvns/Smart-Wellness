# diet_plan_tab.py
import streamlit as st
import pandas as pd
from database import FOOD_DB # Still uses your central food dictionary

def show_diet_plan():
    # Verification logic: Ensures user has used the ML predictor first
    if not st.session_state.user:
        st.error("Please calculate calories in 'Enter Details' first!")
        return

    u = st.session_state.user
    st.title(f"🍽 {u['name']}'s Custom AI Diet Plan")
    
    # Calculate calorie target based on goal
    target = u['cal']
    if u['goal'] == "Lose Weight": target -= 500
    elif u['goal'] == "Gain Weight": target += 500

    # DYNAMIC MEAL SELECTION LOGIC
    diet_choice = u.get('diet', 'Combined')

    if diet_choice == "Pure Veg":
        # 100% Vegetarian options for all meals
        MEALS = {
            "🥣 Breakfast (Oats & Milk)": ["Oats", "Milk", "Banana", "Almonds"],
            "🍛 Lunch (Rice & Soya)": ["Rice", "Soya Chunks", "Spinach", "Carrot"],
            "🍠 Snacks (Energy Focus)": ["Sweet Potato", "Banana"],
            "🍽 Dinner (Roti & Paneer)": ["Paneer", "Rice", "Dal (Lentils)", "Cucumber"]
        }
    elif diet_choice == "Non-Veg":
        # Focused on Non-Veg protein sources
        MEALS = {
            "🥣 Breakfast (Eggs & Milk)": ["Egg", "Milk", "Banana", "Almonds"],
            "🍛 Lunch (Chicken & Rice)": ["Rice", "Chicken Breast", "Spinach", "Carrot"],
            "🍠 Snacks (Protein Focus)": ["Egg", "Banana"],
            "🍽 Dinner (Fish & Veggies)": ["Fish (Tilapia)", "Rice", "Dal (Lentils)", "Cucumber"]
        }
    else: 
        # "Combined": Lunch is Non-Veg, Dinner is Veg as requested
        MEALS = {
            "🥣 Breakfast (Eggs & Oats)": ["Egg", "Oats", "Milk", "Almonds"],
            "🍛 Lunch (Non-Veg Focus)": ["Rice", "Chicken Breast", "Spinach", "Carrot"],
            "🍠 Snacks (Fruit & Nuts)": ["Banana", "Almonds"],
            "🍽 Dinner (Veggie Focus)": ["Paneer", "Rice", "Dal (Lentils)", "Cucumber"]
        }

    st.subheader("📊 Daily Targets")
    c1, c2, c3 = st.columns(3)
    c1.metric("Goal", u['goal'])
    c2.metric("Dietary Type", diet_choice)
    c3.metric("Target Intake", f"{int(target)} kcal/day")

    st.divider()

    for meal, foods in MEALS.items():
        st.subheader(meal)
        
        # Meal calorie distribution logic (25% breakfast, 35% lunch, etc.)
        meal_percentage = 0.25 if "Breakfast" in meal else 0.35 if "Lunch" in meal else 0.15 if "Snacks" in meal else 0.25
        m_cal_target = target * meal_percentage
        
        meal_data = []
        for food_name in foods:
            if food_name in FOOD_DB:
                f = FOOD_DB[food_name]
                
                # Distribute calories across items in the meal
                item_cal_share = m_cal_target / len(foods)
                qty = int((item_cal_share / f['cal']) * 100)
                
                # Accurately calculate values for the table
                protein_val = round(f['pro'] * (qty / 100), 1)
                fiber_val = round(f['fib'] * (qty / 100), 1)
                
                meal_data.append({
                    "Food Item": food_name,
                    "Quantity": f"{qty}g",
                    "Protein (g)": f"{protein_val}g",
                    "Fiber (g)": f"{fiber_val}g",
                    "Calories": f"{int(item_cal_share)} kcal"
                })

        # Display as a professional table
        df_meal = pd.DataFrame(meal_data)
        st.table(df_meal)

    st.success(f"✨ Custom {diet_choice} plan generated based on your fitness goals.")