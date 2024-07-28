import streamlit as st
import sqlite3

def buttons():
    # Adjust display based on login status
    if not st.session_state.get('logged_in', False):
        col1, col2, col3 = st.columns([0.55, 0.1, 0.1])
        col1.write("")

        if col2.button('Login'):
            st.session_state['page'] = 'login'
        
        if col3.button('Sign Up'):
            st.session_state['page'] = 'signup'
    else:
        col1, col2 = st.columns([0.65, 0.1])
        col1.write(f"Welcome, {st.session_state['user_name']}!")

def display_page():
    # Control page display based on session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
    else:
        home_page()

def home_page():
    st.write("Welcome to the Home Page. Select an option from the menu.")

def login_page():
    st.title("Login Page")
    with st.form(key='login_form'):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button and authenticate_user(email, password):
            st.session_state['logged_in'] = True
            st.session_state['user_name'] = email  # Example user display
            st.session_state['page'] = 'home'
        elif submit_button:
            st.error("Login failed. Check your credentials.")

def signup_page():
    st.title("Sign Up Page")
    with st.form(key='signup_form'):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            result = add_user_to_db(name, email, password)
            if result == "success":
                st.success("You have successfully signed up!")
            elif result == "duplicate":
                st.error("This email already exists. Please use a different email or log in.")
            else:
                st.error("Failed to add user. Please try again.")

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
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    db_password = c.fetchone()
    conn.close()
    return db_password and db_password[0] == password

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
        conn.commit()
    except Exception as e:
        print(f"Error creating database table: {e}")
    finally:
        conn.close()

create_database()
