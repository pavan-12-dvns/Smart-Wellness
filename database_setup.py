# database.py
from database_manager import get_db_connection # Removed sqlite3
import streamlit as st

def init_db():
    """
    Initializes the permanent MySQL database schema for the 
    Smart Wellness Recommendation Assistant project.
    """
    conn = get_db_connection()
    if conn is None:
        st.error("Could not connect to MySQL to initialize tables.")
        return
        
    try:
        c = conn.cursor()
        
        # 1. Table for Login Credentials
        # Using VARCHAR(255) for MySQL compatibility
        c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (username VARCHAR(255) PRIMARY KEY, 
                      password VARCHAR(255))''')
        
        # 2. Table for User Profiles (Linked to username)
        # Storing physical metrics and predicted calories permanently
        c.execute('''CREATE TABLE IF NOT EXISTS profiles 
                     (username VARCHAR(255) PRIMARY KEY, 
                      name VARCHAR(255), 
                      age INT, 
                      weight FLOAT, 
                      height FLOAT, 
                      gender VARCHAR(50), 
                      activity INT, 
                      diet VARCHAR(100), 
                      goal VARCHAR(100), 
                      cal INT)''')
        
        # 3. Table for Food Logs (Multiple entries per user)
        # Changed 'AUTOINCREMENT' to MySQL-standard 'AUTO_INCREMENT'
        # Added macro columns to match your Food Calculator logic
        c.execute('''CREATE TABLE IF NOT EXISTS food_logs 
                     (id INT AUTO_INCREMENT PRIMARY KEY, 
                      username VARCHAR(255), 
                      food VARCHAR(255), 
                      qty VARCHAR(100), 
                      protein FLOAT, 
                      carbs FLOAT,
                      fat FLOAT,
                      fiber FLOAT,
                      calories INT, 
                      date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        st.success("MySQL Database Tables Initialized Successfully!")
        
    except Exception as e:
        st.error(f"Initialization Error: {e}")
    finally:
        # Essential to close connection to free up the MySQL pool
        if conn.is_connected():
            conn.close()

# Initialize tables when this script runs
if __name__ == "__main__":
    init_db()