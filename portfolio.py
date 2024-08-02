import sqlite3
import re

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            email TEXT PRIMARY KEY,
            password TEXT
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_stocks (
            email TEXT,
            stock_symbol TEXT,
            PRIMARY KEY (email, stock_symbol),
            FOREIGN KEY (email) REFERENCES users(email)
        )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error creating database tables: {e}")
    finally:
        conn.close()

def add_user_to_db(name, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return "success"
    except sqlite3.IntegrityError:
        return "duplicate"
    except Exception as e:
        print(f"Database error: {e}")
        return "failure"
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("SELECT name, password FROM users WHERE email = ?", (email,))
        user_info = c.fetchone()
        if user_info and user_info[1] == password:
            return True, user_info[0]  # Return True and the user's name
        else:
            return False, None
    finally:
        conn.close()

def load_user_stocks(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("SELECT stock_symbol FROM user_stocks WHERE email = ?", (email,))
        stocks = c.fetchall()
        return [stock[0] for stock in stocks]
    finally:
        conn.close()

def add_stock_to_user(email, stock):
    print("attempting to add stock ", stock, " to user ", email)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO user_stocks (email, stock_symbol) VALUES (?, ?)", (email, stock))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Stock already exists for this user.")
    finally:
        conn.close()

def remove_stock_from_user(email, stock):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("DELETE FROM user_stocks WHERE email = ? AND stock_symbol = ?", (email, stock))
        conn.commit()
    finally:
        conn.close()

# Initialize database tables
create_database()
