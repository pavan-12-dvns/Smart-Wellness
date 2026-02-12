# check_in_tab.py
import streamlit as st
from datetime import datetime
import pytz
from database_manager import get_db_connection # Removed sqlite3

def show_check_in():
    st.title("✅ Daily Compliance Check-In")
    
    if not st.session_state.get('username'):
        st.warning("Please login to log your progress.")
        return

    IST = pytz.timezone('Asia/Kolkata')
    today_ist = datetime.now(IST).strftime('%Y-%m-%d')
    username = st.session_state.username
    
    # Using your centralized MySQL connection helper
    conn = get_db_connection()
    if conn is None:
        st.error("Database connection failed.")
        return
        
    c = conn.cursor()

    # We still check for an entry just to show the user their current status
    # MySQL uses %s as the placeholder instead of ?
    c.execute("SELECT total_score FROM compliance_data WHERE username = %s AND date = %s ORDER BY id DESC LIMIT 1", (username, today_ist))
    row = c.fetchone()

    if row:
        st.info(f"Current recorded score for today: {row[0]}%. You can update it below.")

    with st.form("check_in_form"):
        st.subheader(f"Update Goals for {today_ist}")
        
        f_water = st.radio("Water Goal Met?", ["Yes", "No"], index=1)
        f_diet = st.radio("Diet Followed?", ["Yes", "No"], index=1)
        f_work = st.radio("Workout Done?", ["Yes", "No"], index=1)
        f_sleep = st.radio("Sleep Goal Met?", ["Yes", "No"], index=1)
        
        if st.form_submit_button("Submit & Update Progress"):
            score_count = 0.0
            if f_water == "Yes": score_count += 1.0
            if f_diet == "Yes": score_count += 1.0
            if f_work == "Yes": score_count += 1.0
            if f_sleep == "Yes": score_count += 1.0
            
            # (X / 4) * 100. Example: 1 Yes = 25%.
            final_score = (score_count / 4.0) * 100.0
            
            try:
                # INSERT logic preserved to allow 'n' submissions
                # Placeholders updated to %s for MySQL compatibility
                c.execute('''INSERT INTO compliance_data 
                             (username, date, water, diet, workout, sleep, total_score) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                          (username, today_ist, 
                           100 if f_water=="Yes" else 0, 
                           100 if f_diet=="Yes" else 0, 
                           100 if f_work=="Yes" else 0, 
                           100 if f_sleep=="Yes" else 0, 
                           final_score))
                conn.commit()
                st.success(f"Progress Updated! Latest Score: {final_score}%")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close() # Vital to close connection to prevent MySQL 'too many connections' error
    
    # Final safety close if the form wasn't submitted
    if conn.is_connected():
        conn.close()