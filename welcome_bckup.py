DB_PATH = "users_db.db"
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import os, base64
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
import auth 
import sqlite3

import bcrypt
import time
import uuid
import parents_resources
def set_full_page_background(image_path):
    try:
        if not os.path.exists(image_path):
            st.error(f"Image file '{image_path}' not found.")
            return

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        st.markdown(f"""
            <style>
            [data-testid="stApp"] {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error setting background: {e}")


def auto_slider_with_quotes_and_button(images, quotes, target_page=None, role="Resources", key_prefix=None):
    if key_prefix is None:
        key_prefix = f"slider_{uuid.uuid4().hex}"

    index_key = f"{key_prefix}_index"
    refresh_key = f"{key_prefix}_refresh_{uuid.uuid4().hex[:6]}"  # Ensure unique key
    last_refresh_key = f"{key_prefix}_last_refresh"

    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    total = len(images)
    index = st.session_state[index_key]

    refresh_interval = 10000 if index < total - 1 else 20000
    st_autorefresh(interval=refresh_interval, key=refresh_key)

    if last_refresh_key not in st.session_state or st.session_state[last_refresh_key] != index:
        st.session_state[index_key] = (index + 1) % total
        st.session_state[last_refresh_key] = index

    with open(images[index], "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    quote_text = quotes[index]
    explore_button_text = f"Explore {role} on Mental Health"

    buttons_html = f"""
        <div class="button-group">
            <a href="?page={target_page}"><button type="button">{explore_button_text}</button></a>
            <a href="?page=book_appointment"><button type="button">Book Appointment</button></a>
            <a href="?page=feedback"><button type="button">Give Feedback</button></a>
        </div>
    """

    st.markdown(f"""
        <style>
        .hero {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            height: 75vh;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            text-align: center;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            border-radius: 1px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            flex-direction: column;
        }}
        .overlay-text {{
            font-size: 2.2em;
            font-weight: 600;
            text-shadow: 2px 2px 6px black;
            margin-bottom: 20px;
        }}
        .button-group {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }}
        .button-group button {{
            background-color: #00897b;
            color: white;
            padding: 12px 28px;
            border-radius: 25px;
            border: none;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .button-group button:hover {{
            background-color: red;
            color: black;
        }}
        </style>

        <div class="hero">
            <div class="overlay-text">{quote_text}</div>
            {buttons_html}
        </div>
    """, unsafe_allow_html=True)

def styled_subheader(text):
    st.markdown(f"""
    <div style="
        border: 3px solid;
        border-image-slice: 1;
        border-width: 3px;
        border-image-source: linear-gradient(to right, #b2dfdb, #e1bee7);
        border-radius: 10px;
        padding: 12px 20px;
        color: #2c3e50;
        font-size: 26px;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
        margin-top: 20px;
        margin-bottom: 4px;
        width: 100%;
        max-width: 100vw;
        box-sizing: border-box;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        display: block;
        background-color: skyblue;
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)

def home_page():
    styled_subheader("🎓 Mental Health Resources for Students")
    student_images = ['images/std.jpg', 'images/std3.jpg', 'images/std4.jpg']
    student_quotes = [
        "Your mind matters as much as your grades.",
        "Strong minds ask for help. That’s real strength.",
        "Healthy minds. Safe spaces. Stronger schools."]
    auto_slider_with_quotes_and_button(student_images, student_quotes, target_page="students")
    
    styled_subheader("👩‍🏫 Mental Health Resources for Teachers")
    teacher_images = ['images/std3.jpg', 'images/std4.jpg', 'images/std3.jpg']
    teacher_quotes = [
        "Support your students by supporting yourself.",
        "A healthy mind creates a healthy classroom.",
        "Strong teachers build stronger communities."]
    auto_slider_with_quotes_and_button(teacher_images, teacher_quotes, target_page="teachers", key_prefix="teacher_slider")
    st.markdown("---")
    styled_subheader("👨‍👩‍👧 Mental Health Resources for Parents")
    parent_images = ['images/std2.jpg', 'images/psy4.jpg', 'images/std3.jpg']
    parent_quotes = [
        "Your child's mental health starts with a caring home.",
        "Listening is the first step to supporting your child.",
        "Together, we can create a safe environment for your family."
    ]
    auto_slider_with_quotes_and_button(parent_images, parent_quotes, target_page="parents", key_prefix="parent_slider")


# ================== MAIN ROUTER ==================
def main():
    query_params = st.query_params 
    current_page = query_params.get("page", "home")

    if current_page == "home":
        home_page()
    elif current_page == "parents":
        if st.button("⬅ Back to Home"):
            st.query_params.update({"page": "home"}) 
            st.rerun()
        parents_resources.main()
    

    elif current_page == "students":
        if st.button("⬅ Back to Home"):
            st.query_params.update({"page": "home"})
            st.rerun()
        parents_resources.main()
    

    elif current_page == "teachers":
        if st.button("⬅ Back to Home"):
            st.query_params.update({"page": "home"})
            st.rerun()
        parents_resources.main()


if __name__ == "__main__":
    main()
