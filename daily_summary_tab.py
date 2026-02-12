# daily_summary_tab.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
from database_manager import get_db_connection # Removed sqlite3

def show_daily_summary():
    st.title("📊 Consumption Dashboard")
    
    if not st.session_state.get('username'):
        st.warning("Please login to see your summary.")
        return

    # --- IST TIMEZONE FIX: Ensuring strict Hyderabad local time ---
    # This logic is critical for the 12:00 AM reset in Hyderabad
    IST = pytz.timezone('Asia/Kolkata')
    today_ist = datetime.now(IST).strftime('%Y-%m-%d')
    
    # Using your centralized MySQL connection
    conn = get_db_connection()
    if conn is None:
        st.error("Database connection failed.")
        return
        
    username = st.session_state.username
    
    # MYSQL UPDATED QUERY: 
    # 1. Changed placeholders from ? to %s
    # 2. MySQL date() function used to filter the IST date string
    query = """SELECT food, qty, protein, carbs, fat, fiber, calories, date 
               FROM food_logs 
               WHERE username = %s AND date(date) = %s"""
    
    try:
        # Passes the calculated IST date directly into the MySQL filter
        df = pd.read_sql_query(query, conn, params=(username, today_ist))
    except Exception as e:
        st.error(f"Database Error: {e}")
        df = pd.DataFrame()
    finally:
        # Crucial to close MySQL connection to prevent server lockout
        if conn.is_connected():
            conn.close()

    # Dashboard logic preserved for the Feb 12 reset
    if df.empty:
        st.warning(f"Dashboard Reset: No food logged yet for today ({today_ist}).")
        return

    # Pie chart and Table logic fully preserved
    df.columns = ['Food', 'Quantity', 'Protein', 'Carbs', 'Fat', 'Fiber', 'Calories', 'Date']
    
    # Ensuring numeric types for Plotly calculations
    df['Protein'] = pd.to_numeric(df['Protein']).fillna(0)
    df['Carbs'] = pd.to_numeric(df['Carbs']).fillna(0)
    df['Fat'] = pd.to_numeric(df['Fat']).fillna(0)
    df['Fiber'] = pd.to_numeric(df['Fiber']).fillna(0)
    
    totals = {
        "Protein": df['Protein'].sum(), 
        "Carbs": df['Carbs'].sum(), 
        "Fats": df['Fat'].sum(), 
        "Fiber": df['Fiber'].sum()
    }

    if sum(totals.values()) > 0:
        st.subheader(f"🍕 Daily Macro-Nutrient Distribution for {today_ist} (%)")
        pie_df = pd.DataFrame({"Nutrient": list(totals.keys()), "Grams": list(totals.values())})
        
        # Plotly logic and visual fixes preserved exactly as requested
        fig = px.pie(pie_df, values='Grams', names='Nutrient', hole=0.4)
        
        fig.update_traces(
            textinfo='percent', 
            textposition='inside',
            insidetextorientation='horizontal'
        )
        fig.update_layout(showlegend=True)
        
        st.plotly_chart(fig, use_container_width=True)

    # Detailed data view for Osmania University project report
    st.subheader(f"📋 Consumed Food Details ({today_ist})")
    st.dataframe(df, use_container_width=True)