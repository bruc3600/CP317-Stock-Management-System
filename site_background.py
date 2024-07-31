import streamlit as st
import base64

def get_base64_of_file(path):
    with open(path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    return encoded

def background():
    # Path to your image file
    image_path = 'background.jpg'  # Change this to your local path
    image_string = get_base64_of_file(image_path)

    # HTML to inject contained within a Python multiline string
    background_image_html = f"""
    <style>
    body, html {{
        height: 100%;
        margin: 0;
    }}

    .stApp {{
        height: 100%;
        background: url("data:image/jpeg;base64,{image_string}") no-repeat center center fixed; 
        background-size: cover;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    </style>
    """

    # Inject HTML with markdown
    st.markdown(background_image_html, unsafe_allow_html=True)
