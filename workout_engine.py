# workout_engine.py
import streamlit as st
import pandas as pd
from database_manager import get_db_connection # Removed sqlite3

def show_workout_recommendation():
    st.title("🏋️ Smart AI Workout Engine")
    
    # Validation: Ensure user is logged in for data isolation
    if not st.session_state.get('username'):
        st.warning("Please login to generate your personalized workout plan.")
        return

    username = st.session_state.username
    conn = get_db_connection() # Using centralized MySQL connection
    if conn is None:
        st.error("Database connection failed.")
        return
    c = conn.cursor()

    # --- SQL LOGIC: ENSURE COLUMNS EXIST FOR PERSISTENCE ---
    # MySQL handles column checks slightly differently than SQLite
    try:
        # Changed placeholder from ? to %s
        c.execute("SELECT workout_level, workout_goal, workout_days, workout_vars FROM profiles WHERE username = %s", (username,))
    except Exception:
        # Dynamically add columns for MySQL if they don't exist in the profiles table
        try:
            c.execute("ALTER TABLE profiles ADD COLUMN workout_level VARCHAR(100)")
            c.execute("ALTER TABLE profiles ADD COLUMN workout_goal VARCHAR(100)")
            c.execute("ALTER TABLE profiles ADD COLUMN workout_days INT")
            c.execute("ALTER TABLE profiles ADD COLUMN workout_vars INT")
            conn.commit()
        except Exception:
            pass # Columns likely already exist
    
    # Fetch existing saved plan
    c.execute("SELECT workout_level, workout_goal, workout_days, workout_vars FROM profiles WHERE username = %s", (username,))
    saved_plan = c.fetchone()

    with st.form("workout_form"):
        # Set default values from database if they exist
        def_level = saved_plan[0] if saved_plan and saved_plan[0] else "Beginner"
        def_goal = saved_plan[1] if saved_plan and saved_plan[1] else "Muscle Build"
        def_days = saved_plan[2] if saved_plan and saved_plan[2] else 4
        def_vars = saved_plan[3] if saved_plan and saved_plan[3] else 4

        level = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(def_level))
        goal = st.selectbox("Your Goal", ["Muscle Build", "Fat Loss"], index=["Muscle Build", "Fat Loss"].index(def_goal))
        
        day_options = [3, 4, 5, 6]
        days = st.selectbox("Workout Days per Week", day_options, index=day_options.index(def_days))
        
        num_vars = st.number_input("Variations per muscle (3-5)", 3, 5, value=def_vars)
        submit = st.form_submit_button("Generate Optimized Plan")

    # Display plan if submitted OR if a saved plan already exists
    if submit or (saved_plan and saved_plan[0]):
        if submit:
            # Save selection to user profile in MySQL using %s
            c.execute("""UPDATE profiles SET workout_level = %s, workout_goal = %s, 
                         workout_days = %s, workout_vars = %s WHERE username = %s""", 
                      (level, goal, days, num_vars, username))
            conn.commit()
        else:
            # Use saved values if page was just refreshed
            level, goal, days, num_vars = saved_plan

        # --- SMART SPLIT SELECTION LOGIC (Logic fully preserved) ---
        if days == 3:
            split_type = "Full Body"
            daily_focus = ["Full Body"] * 3
        elif days == 4:
            split_type = "Upper/Lower"
            daily_focus = ["Upper Body", "Lower Body", "Upper Body", "Lower Body"]
        elif days == 5:
            if level == "Advanced":
                split_type = "Bro Split (Single Muscle)"
                daily_focus = ["Chest", "Back", "Shoulders", "Legs", "Arms"]
            else:
                split_type = "Push/Pull/Legs + Upper/Lower"
                daily_focus = ["Push", "Pull", "Legs", "Upper Body", "Lower Body"]
        else: # 6 Days
            split_type = "Push/Pull/Legs (PPL)"
            daily_focus = ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]

        st.success(f"✅ AI Recommendation: **{split_type}** is best for your {level} level.")
        st.divider()

        # Database of exercises
        db = {
            "Chest": ["Bench Press", "Incline DB Press", "Chest Flys", "Push-ups", "Dips"],
            "Back": ["Deadlifts", "Lat Pulldowns", "Bent Over Rows", "Pull-ups", "Cable Rows"],
            "Shoulders": ["Overhead Press", "Lateral Raises", "Front Raises", "Face Pulls", "Reverse Flys"],
            "Arms": ["Barbell Curls", "Hammer Curls", "Tricep Pushdowns", "Skull Crushers", "Preacher Curls"],
            "Legs": ["Squats", "Leg Press", "Leg Extensions", "Hamstring Curls", "Calf Raises"]
        }

        rep_range = "8-12" if goal == "Muscle Build" else "15-20"

        # Generate separate tables for each day
        for i, focus in enumerate(daily_focus):
            st.markdown(f"### 🗓 Day {i+1}: {focus}")
            
            # Logic to pick exercises based on focus name
            if focus == "Full Body":
                ex_list = [db["Chest"][0], db["Back"][0], db["Legs"][0], db["Shoulders"][0], db["Arms"][0]]
            elif focus == "Upper Body":
                ex_list = [db["Chest"][1], db["Back"][1], db["Shoulders"][1], db["Arms"][1], db["Back"][2]]
            elif focus == "Lower Body":
                ex_list = [db["Legs"][1], db["Legs"][2], db["Legs"][3], db["Legs"][4], db["Legs"][0]]
            elif focus == "Push":
                ex_list = [db["Chest"][0], db["Shoulders"][0], db["Arms"][2], db["Chest"][3], db["Shoulders"][2]]
            elif focus == "Pull":
                ex_list = [db["Back"][0], db["Back"][2], db["Arms"][0], db["Back"][3], db["Arms"][1]]
            else: # Specific muscle (Bro Split)
                ex_list = db[focus]

            selected = ex_list[:num_vars]
            df = pd.DataFrame({
                "Exercise": selected,
                "Sets": ["4"] * len(selected),
                "Reps": [rep_range] * len(selected)
            })
            st.table(df)
            
    # Final safety close to prevent connection leakage
    if conn.is_connected():
        conn.close()