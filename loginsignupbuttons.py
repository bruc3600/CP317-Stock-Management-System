import streamlit as st
import sqlite3
import re

def buttons():
    # Adjust display based on login status
    if not st.session_state.get('logged_in', False):
        col1, col2, col3 = st.columns([0.55, 0.1, 0.1])
        col1.write("")

        # Ensure buttons have unique keys to prevent DuplicateWidgetID error
        if col2.button('Login', key='login_button'):
            st.session_state['page'] = 'login'
        
        if col3.button('Sign Up', key='signup_button'):
            st.session_state['page'] = 'signup'
    else:
        col1, col2 = st.columns([0.65, 0.1])
        col1.write(f"Welcome, {st.session_state['user_name']}!")

def display_page():
    # Ensure 'page' state initialization
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

    # Page rendering based on session state
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
        email = st.text_input("Email", key='login_email')
        password = st.text_input("Password", type="password", key='login_password')
        submit_button = st.form_submit_button("Login")

        if submit_button:
            authenticated, user_name = authenticate_user(email, password)  # Now returns a tuple
            if authenticated:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user_name  # declare the user's name
                st.session_state['page'] = 'home'
                st.session_state['user_email'] = email # declare email in session state as user_email to be used
                st.success(f"You have successfully logged in, {user_name}!")  # Include user's name in the message
            else:
                st.error("Login failed. Check your credentials.")



def signup_page():
    st.title("Sign Up Page")
    with st.form(key='signup_form'):
        name = st.text_input("Name", key='signup_name')
        email = st.text_input("Email", key='signup_email')
        password = st.text_input("Password", type="password", key='signup_password')
        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            error_messages = []

            # Email validation
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                error_messages.append("Invalid email format. Please enter a valid email address.")

            # Password length check
            if len(password) < 8:
                error_messages.append("Password must be at least 8 characters long.")

            # Display all accumulated error messages
            if error_messages:
                for error in error_messages:
                    st.error(error)
                return  # Return after displaying all errors to avoid further processing

            # Attempt to add user to database
            result = add_user_to_db(name, email, password)
            if result == "success":
                st.success("You have successfully signed up!")
                st.session_state['page'] = 'home'
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = name
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
    try:
        c.execute("SELECT name, password FROM users WHERE email = ?", (email,))
        user_info = c.fetchone()
        if user_info and user_info[1] == password:
            return True, user_info[0]  # Return True and the user's name
        else:
            return False, None
    finally:
        conn.close()

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