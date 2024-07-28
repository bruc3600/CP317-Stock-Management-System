import streamlit as st

def buttons():
    # Check if the user is logged in and adjust the display accordingly
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
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
    # Redirect to the home page after login or initial load
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
    else:
        home_page()

def home_page():
    st.write("This is the Home Page. Choose an option above if not logged in or enjoy the content.")

def login_page():
    st.title("Login Page")
    form = st.form(key='login_form')
    email = form.text_input("Email")
    password = form.text_input("Password", type="password")
    submit_button = form.form_submit_button("Login")

    if submit_button:
        # Dummy authentication mechanism
        if authenticate_user(email, password):
            st.session_state['logged_in'] = True
            st.session_state['user_name'] = email  # Simulating user's name as email
            st.session_state['page'] = 'home'
        else:
            st.error("Login failed. Check your credentials.")

def signup_page():
    st.title("Sign Up Page")
    st.write("Sign up functionality not implemented yet.")

def authenticate_user(email, password):
    # This is a dummy function to simulate authentication
    # In real scenarios, this should check against a database or authentication service
    return email == "user@example.com" and password == "password"

# Entry point for the application
if __name__ == '__main__':
    buttons()
    display_page()
