import streamlit as st
import base64

def get_base64_of_file(path):
    with open(path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    return encoded

def background():
    # Path to your video file
    video_path = 'background.mp4'  # Change this to your local path
    video_string = get_base64_of_file(video_path)

    # HTML to inject contained within a Python multiline string
    background_video_html = f"""
    <style>
    body, html {{
        height: 100%;
        margin: 0;
    }}

    .stApp {{
        height: 100%;
        background: no-repeat center center fixed; 
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .background_video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%; 
        min-height: 100%;
        width: auto; 
        height: auto; 
        z-index: -100;
        background-size: cover;
        overflow: hidden;
    }}
    </style>
    <video class="background_video" autoplay loop muted>
        <source src="data:video/mp4;base64,{video_string}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """

    # Inject HTML with markdown
    st.markdown(background_video_html, unsafe_allow_html=True)
