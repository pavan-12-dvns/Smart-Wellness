# analytics_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
from database_manager import get_db_connection # Removed sqlite3

def show_analytics():
    st.title("📈 Overall Wellness Progress")
    
    if not st.session_state.get('username'):
        st.warning("Please login to view your progress analytics.")
        return

    username = st.session_state.username
    conn = get_db_connection() # Using centralized MySQL connection
    
    if conn is None:
        st.error("Could not connect to the database.")
        return
    
    try:
        # --- MYSQL COMPATIBLE QUERY ---
        # Logic preserved: Picks the highest ID for each date to remove the vertical line bug
        comp_query = """
            SELECT date, water, diet, workout, sleep, total_score 
            FROM compliance_data 
            WHERE username = %s 
            AND id IN (SELECT MAX(id) FROM compliance_data GROUP BY date)
            ORDER BY date ASC
        """
        
        # In MySQL, we use %s instead of ? for placeholders
        df_comp = pd.read_sql_query(comp_query, conn, params=(username,))
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        df_comp = pd.DataFrame()
    finally:
        conn.close() # Always close the MySQL connection

    if df_comp.empty:
        st.warning("Please complete your 'Daily Check-In' to see your progress graph!")
    else:
        # Standardize columns for Plotly
        df_comp.columns = ['Date', 'Water', 'Diet', 'Workout', 'Sleep', 'Total Score']
        df_comp['Date'] = pd.to_datetime(df_comp['Date']).dt.date

        st.divider()
        st.subheader("🎯 Daily Wellness Score Trend")
        
        # Plotting the clean trend line
        fig_overall = px.line(
            df_comp, 
            x='Date', 
            y='Total Score', 
            markers=True, 
            line_shape='linear', 
            color_discrete_sequence=['#4CAF50']
        )
        
        # Y-axis fixed from 0 to 100
        fig_overall.update_yaxes(range=[0, 105], title="Wellness Score (1-100)")
        fig_overall.update_xaxes(type='category', title="Check-In Dates")
        
        st.plotly_chart(fig_overall, use_container_width=True)

        st.divider()
        # Calculate performance for your Osmania University project report
        avg_score = round(df_comp['Total Score'].mean(), 1)
        st.metric("Total Average Performance", f"{avg_score}%")