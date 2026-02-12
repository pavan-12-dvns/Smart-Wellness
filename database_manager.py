# database_manager.py
import mysql.connector
import streamlit as st

def get_db_connection():
    """
    Connects to your permanent MySQL Cloud Database.
    Credentials are stored safely in Streamlit Secrets.
    """
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASS"],
            database=st.secrets["DB_NAME"],
            port=st.secrets.get("DB_PORT", 3306)
        )
    except Exception as e:
        st.error(f"Failed to connect to MySQL: {e}")
        return None

def init_db():
    """Initializes tables using MySQL syntax (AUTO_INCREMENT)."""
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        # MySQL uses VARCHAR and AUTO_INCREMENT
        c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS compliance_data 
                     (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), 
                      date DATE, water INT, diet INT, workout INT, 
                      sleep INT, total_score FLOAT)''')
        conn.commit()
        conn.close()