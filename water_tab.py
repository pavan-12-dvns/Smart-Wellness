# water_tab.py
import streamlit as st
from datetime import datetime
import pytz
from database_manager import get_db_connection # Removed sqlite3

def show_water_tracker():
    st.title("💧 Smart Hydration Tracker")
    
    if not st.session_state.user:
        st.error("Please enter your personal details in 'Enter Details' first to set your water goal!")
        return

    # --- IST TIMEZONE FIX ---
    # Ensures the reset happens at 12:00 AM Hyderabad time
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).strftime('%Y-%m-%d')
    
    username = st.session_state.username
    conn = get_db_connection() # Using centralized MySQL connection
    if conn is None:
        st.error("Database connection failed.")
        return
        
    c = conn.cursor()
    
    # Ensure table exists using MySQL syntax
    c.execute('''CREATE TABLE IF NOT EXISTS water_history 
                 (username VARCHAR(255), date DATE, consumed INT, 
                  PRIMARY KEY(username, date))''')
    conn.commit()

    # Fetch today's record
    # MySQL uses %s instead of ?
    c.execute("SELECT consumed FROM water_history WHERE username = %s AND date = %s", (username, today))
    result = c.fetchone()
    
    if result:
        st.session_state.daily_water_consumed = result[0]
    else:
        st.session_state.daily_water_consumed = 0
        # MySQL "INSERT IGNORE" logic preserved
        c.execute("INSERT IGNORE INTO water_history (username, date, consumed) VALUES (%s, %s, %s)", 
                  (username, today, 0))
        conn.commit()

    # Logic fully preserved: Weight * 35ml per kg
    user_weight = st.session_state.user['w']
    water_goal_ml = user_weight * 35 
    water_goal_liters = round(water_goal_ml / 1000, 2)

    st.subheader(f"Your Daily Goal: {water_goal_liters} Liters ({int(water_goal_ml)} ml)")
    
    progress = min(st.session_state.daily_water_consumed / water_goal_ml, 1.0)
    st.progress(progress)
    
    col1, col2 = st.columns(2)
    col1.metric("Consumed Today", f"{st.session_state.daily_water_consumed} ml")
    col2.metric("Remaining", f"{max(0, int(water_goal_ml - st.session_state.daily_water_consumed))} ml")

    st.divider()
    st.write("### Log Water Intake")
    c1, c2, c3 = st.columns(3)
    
    # Database update helper optimized for MySQL
    def update_water_db(amount):
        new_total = st.session_state.daily_water_consumed + amount
        # Placeholders updated to %s
        c.execute("UPDATE water_history SET consumed = %s WHERE username = %s AND date = %s", 
                  (new_total, username, today))
        conn.commit()
        st.session_state.daily_water_consumed = new_total

    # Button logic preserved exactly
    if c1.button("+ 150ml"):
        update_water_db(150)
        conn.close()
        st.rerun()
    if c2.button("+ 200ml"):
        update_water_db(200)
        conn.close()
        st.rerun()
    if c3.button("+ 500ml"):
        update_water_db(500)
        conn.close()
        st.rerun()

    custom_amt = st.number_input("Add custom amount (ml):", min_value=0, step=50)
    if st.button("Add Custom"):
        update_water_db(custom_amt)
        conn.close()
        st.success(f"Added {custom_amt}ml!")
        st.rerun()

    if st.button("🗑️ Reset Daily Total"):
        # Reset logic preserved
        c.execute("UPDATE water_history SET consumed = 0 WHERE username = %s AND date = %s", (username, today))
        conn.commit()
        st.session_state.daily_water_consumed = 0
        conn.close()
        st.rerun()
        
    # Final safety close to prevent MySQL connection leakage
    if conn.is_connected():
        conn.close()