import streamlit as st
import pickle
import pandas as pd
import os
import json
import pytz
from datetime import datetime

# --- DATABASE CONNECTION (Centralized) ---
def get_db_connection():
    import mysql.connector
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"],
        autocommit=True
    )

def init_db():
    """Initializes tables using MySQL specific syntax."""
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        # MySQL uses VARCHAR and AUTO_INCREMENT
        c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255))''')
        c.execute('''CREATE TABLE IF NOT EXISTS profiles 
                     (username VARCHAR(255) PRIMARY KEY, name VARCHAR(255), age INT, 
                      weight FLOAT, height FLOAT, gender VARCHAR(50), 
                      act_val INT, diet VARCHAR(100), goal VARCHAR(100), cal INT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS food_logs 
                     (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), food VARCHAR(255), 
                      qty VARCHAR(100), protein FLOAT, carbs FLOAT, fat FLOAT, fiber FLOAT, 
                      calories INT, date DATETIME)''')
        conn.close()

# Start database on initialization
init_db()

# --- CUSTOM MODULE IMPORTS ---
try:
    import daily_summary_tab as ds_tab
    import diet_plan_tab as dp_tab
    import workout_engine as workout
    import water_tab as water
    import check_in_tab as checkin
    import analytics_dashboard as analytics
    from database import FOOD_DB
except ImportError as e:
    st.error(f"Missing module error: {e}")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Wellness Assistant", 
    layout="wide", 
    initial_sidebar_state="auto"
)

# --- CSS (Mobile Responsiveness Preserved) ---
st.markdown("""
    <style>
    .block-container { padding-top: 3.5rem !important; }
    .main { background-color: #0e1117; color: white; }
    .main-title { font-size: 2.5rem !important; color: #4CAF50; text-align: center; font-weight: bold; }
    .subtitle { font-size: 1.2rem !important; color: #BDC3C7; text-align: center; margin-bottom: 25px; }
    div.stButton > button {
        width: 100%; border-radius: 5px; height: 3em; 
        background-color: transparent !important; color: #4CAF50 !important; 
        border: 2px solid #4CAF50 !important; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #4CAF50 !important; color: white !important; }

    @media (max-width: 768px) {
        [data-testid="stSidebar"] { width: 80vw !important; }
        .main-title { font-size: 1.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = None
if 'user' not in st.session_state: st.session_state.user = None

# --- ML MODEL LOADING ---
@st.cache_resource
def load_ml():
    if os.path.exists('wellness_model.pkl'):
        try:
            with open('wellness_model.pkl', 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

model = load_ml()

# --- NAVIGATION ---
st.sidebar.title("🏥 Navigation")
if not st.session_state.logged_in:
    page = st.sidebar.radio("Go to", ["Home", "Login / Sign Up"])
else:
    page = st.sidebar.radio("Go to", [
        "Home", "Enter Details", "Food Calculator", "Daily Summary", 
        "Diet Plan", "Workout Recommendation", "Water Tracker", 
        "Daily Check-In", "Progress Dashboard", "Logout"
    ])

# --- PAGE LOGIC ---
if page == "Home":
    st.markdown('<p class="main-title">Smart Wellness Recommendation Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your AI-Powered Guide to Peak Performance and Health</p>', unsafe_allow_html=True)
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🤖 **AI Driven**")
        st.write("Personalized recommendations using Random Forest ML models.")
    with col2:
        st.markdown("### 🥗 **Smart Nutrition**")
        st.write("Dynamic diet plans that adapt to your fitness goals.")
    with col3:
        st.markdown("### 📈 **Live Tracking**")
        st.write("Real-time progress dashboards for wellness metrics.")

elif page == "Login / Sign Up":
    st.title("🔐 User Authentication")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        l_user = st.text_input("Username", key="l_u")
        l_pass = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            conn = get_db_connection(); c = conn.cursor()
            # Changed ? to %s for MySQL
            c.execute("SELECT password FROM accounts WHERE username=%s", (l_user,))
            res = c.fetchone()
            if res and res[0] == l_pass:
                st.session_state.logged_in = True
                st.session_state.username = l_user
                c.execute("SELECT * FROM profiles WHERE username=%s", (l_user,))
                p = c.fetchone()
                if p:
                    st.session_state.user = {
                        "name": p[1], "age": p[2], "w": p[3], "h": p[4], "gen": p[5], 
                        "act_val": p[6], "diet": p[7], "goal": p[8], "cal": p[9]
                    }
                conn.close(); st.success(f"Welcome back, {l_user}!"); st.rerun()
            else:
                conn.close(); st.error("Incorrect Username or Password")
    with tab2:
        s_user = st.text_input("New Username", key="s_u")
        s_pass = st.text_input("New Password", type="password", key="s_p")
        if st.button("Sign Up"):
            if s_user and s_pass:
                conn = get_db_connection(); c = conn.cursor()
                try:
                    c.execute("INSERT INTO accounts (username, password) VALUES (%s, %s)", (s_user, s_pass))
                    conn.commit(); st.success("Account created successfully! Please switch to Login tab.")
                except Exception: st.warning("Username already exists!")
                finally: conn.close()
            else: st.error("Fields cannot be empty")

elif page == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user = None
    st.rerun()

elif st.session_state.logged_in:
    if page == "Enter Details":
        st.title("🧑‍⚕️ User Profile")
        if model is None: st.error("Model file 'wellness_model.pkl' not found!")
        curr = st.session_state.user if st.session_state.user else {}
        with st.form("ml_form"):
            name = st.text_input("Full Name", value=curr.get("name", ""))
            age = st.number_input("Age", 15, 90, value=int(curr.get("age", 25)))
            w = st.number_input("Weight (kg)", 30.0, 200.0, value=float(curr.get("w", 70.0)))
            h = st.number_input("Height (cm)", 120.0, 220.0, value=float(curr.get("h", 175.0)))
            genders = ["Male", "Female"]
            gen = st.selectbox("Gender", genders, index=genders.index(curr.get("gen", "Male")))
            acts = ["1: Sedentary", "2: Lightly Active", "3: Moderately Active", "4: Very Active", "5: Extra Active"]
            act_label = st.selectbox("Activity Level", acts, index=next((i for i, s in enumerate(acts) if s.startswith(str(curr.get("act_val", 3)))), 2))
            diets = ["Pure Veg", "Non-Veg", "Combined"]
            diet_pref = st.selectbox("Dietary Preference", diets, index=diets.index(curr.get("diet", "Combined")))
            goals = ["Maintain Weight", "Lose Weight", "Gain Weight"]
            goal = st.selectbox("Your Goal", goals, index=goals.index(curr.get("goal", "Maintain Weight")))
            if st.form_submit_button("Save & Predict"):
                act_val = int(act_label.split(":")[0])
                gender_val = 1 if gen == "Male" else 0
                if model:
                    pred = int(model.predict([[age, w, h, gender_val, act_val]])[0])
                    st.session_state.user = {"name": name, "age": age, "w": w, "h": h, "gen": gen, "act_val": act_val, "diet": diet_pref, "goal": goal, "cal": pred}
                    conn = get_db_connection(); c = conn.cursor()
                    # Updated for MySQL REPLACE/INSERT syntax
                    c.execute('''REPLACE INTO profiles (username, name, age, weight, height, gender, act_val, diet, goal, cal) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (st.session_state.username, name, age, w, h, gen, act_val, diet_pref, goal, pred))
                    conn.commit(); conn.close(); st.success(f"Profile saved for {name}!")

    elif page == "Food Calculator":
        st.title("🍏 Food Macro Checker & Logger")
        LIQUID_ITEMS = ["Milk", "Curd (Dahi)", "Whey Protein", "Olive Oil", "Orange Juice", "Apple Juice", "Sugarcane Juice"]
        f_choice = st.selectbox("Select Item", list(FOOD_DB.keys()))
        unit = "ml" if f_choice in LIQUID_ITEMS else "Grams"
        quantity = st.number_input(f"Enter Quantity ({unit})", 10, 2000, 100)
        f_data = FOOD_DB[f_choice]; factor = quantity / 100
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Calories", f"{int(f_data['cal'] * factor)} kcal")
        c2.metric("Protein", f"{round(f_data['pro'] * factor, 1)}g")
        c3.metric("Carbs", f"{round(f_data['carb'] * factor, 1)}g")
        c4.metric("Fats", f"{round(f_data['fat'] * factor, 1)}g")
        c5.metric("Fiber", f"{round(f_data['fib'] * factor, 1)}g")
        if st.button("➕ Add to Daily History"):
            IST = pytz.timezone('Asia/Kolkata')
            timestamp_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            conn = get_db_connection(); c = conn.cursor()
            c.execute('''INSERT INTO food_logs (username, food, qty, protein, carbs, fat, fiber, calories, date) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                      (st.session_state.username, f_choice, f"{quantity}{unit}", round(f_data['pro']*factor, 1), round(f_data['carb']*factor, 1), round(f_data['fat']*factor, 1), round(f_data['fib']*factor, 1), int(f_data['cal']*factor), timestamp_ist))
            conn.commit(); conn.close(); st.success(f"Added {f_choice} to history!")

    elif page == "Daily Summary": ds_tab.show_daily_summary()
    elif page == "Diet Plan": dp_tab.show_diet_plan()
    elif page == "Workout Recommendation": workout.show_workout_recommendation()
    elif page == "Water Tracker": water.show_water_tracker()
    elif page == "Daily Check-In": checkin.show_check_in()
    elif page == "Progress Dashboard": analytics.show_analytics()

else:
    st.info("Please Login or Sign Up to access the Smart Wellness tools.")