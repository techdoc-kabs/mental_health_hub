import streamlit as st
from streamlit_card import card
import student_tool_page
import streamlit as st
import base64
import os
import datetime
from datetime import datetime
import cont
from streamlit_javascript import st_javascript
import contact_form
import time
import pandas as pd
from supabase import create_client, Client
import hashlib
import streamlit as st

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from supabase import Client
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def set_full_page_background(image_path):
    try:
        if not os.path.exists(image_path):
            st.error(f"Image file '{image_path}' not found.")
            return
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        st.markdown(
            f"""
            <style>
            [data-testid="stApp"] {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error setting background: {e}")


def fetch_student_details_by_username(username: str, supabase: Client):
    """
    Fetch student/user details from Supabase by username.
    """
    try:
        res = supabase.from_("users").select("*").eq("username", username).execute()
        if res.data:
            return res.data[0]  # first matching record
        return {}
    except Exception as e:
        st.error(f"⚠️ Unexpected error fetching student details: {e}")
        return {}


def student_menu():
    from streamlit_javascript import st_javascript
    device_width = st_javascript("window.innerWidth", key="scren_widith")
    if device_width is None:
        st.stop()
    is_mobile = device_width < 704
    cols_per_row = 4 if not is_mobile else 1
    card_height = "180px" if is_mobile else "220px"
    card_width = "100%" if is_mobile else "100%"
    font_size_title = "50px" if is_mobile else "90px"
    font_size_text = "20px" if is_mobile else "30px"
    with st.expander(f'#### :red[STUDENTS]', expanded= True):
        pages = [
    
    {"title": "📚",  "text":"Resources", "key": "content"},
    {"title": '📝',  "text":"Tasks", "key": "tasks"},
    {"title": "🙋‍♀️",  "text":"Find help", "key": "selfhelp"},
    {"title": "🎋",  "text":"Feedback", "key": "feedback"}
]

    rows = [pages[i:i + cols_per_row] for i in range(0, len(pages), cols_per_row)]
    card_colors = [
        "linear-gradient(135deg, #1abc9c, #16a085)",
        "linear-gradient(135deg, #3498db, #2980b9)",
        "linear-gradient(135deg, #9b59b6, #8e44ad)",
        "linear-gradient(135deg, #e67e22, #d35400)",
        "linear-gradient(135deg, #e74c3c, #c0392b)",
    ]
    rows = [pages[i:i + cols_per_row] for i in range(0, len(pages), cols_per_row)]
    for row_idx, row in enumerate(rows):
        cols = st.columns(cols_per_row, gap="small")
        for col_idx, (col, item) in enumerate(zip(cols, row)):
            color = card_colors[(row_idx * cols_per_row + col_idx) % len(card_colors)]
            with col:
                clicked = card(
                    title=item["title"],
                    text=item["text"],
                    key=item["key"],
                    styles={
                        "card": {
                            "width": card_width,
                            "height": card_height,
                            "border-radius": "10px",
                            "background": color,
                            "color": "white",
                            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                            "border": "0.1px solid #600000",
                            "text-align": "center",
                            "padding": "10px",
                            "margin": "0",
                        },
                        "title": {
                            "font-family": "serif",
                            "font-size": font_size_title,
                        },
                        "text": {
                            "font-family": "serif",
                            "font-size": font_size_text,
                        },
                    }
                )

                if clicked:
                    st.session_state.student_action = item["text"].lower()
                    st.rerun()
CARD_COLORS = [
    "linear-gradient(135deg, #1abc9c, #16a085)",
    "linear-gradient(135deg, #3498db, #2980b9)",
    "linear-gradient(135deg, #9b59b6, #8e44ad)",
    "linear-gradient(135deg, #e67e22, #d35400)",
    "linear-gradient(135deg, #e74c3c, #c0392b)",]

def display_card_menu(page_title, options, selected_key, num_cols=3):
    if f"{selected_key}_just_clicked" not in st.session_state:
        st.session_state[f"{selected_key}_just_clicked"] = False
    device_width = st_javascript("window.innerWidth", key=f"device_width_{selected_key}")
    if device_width is None:
        st.stop()
    is_mobile = device_width < 704
    num_cols_app = num_cols if not is_mobile else 1
    card_height = "150px" if is_mobile else "200px"
    card_width = "100%"
    font_size_title = "50px" if is_mobile else "70px"
    font_size_text = "25px"
    cols = st.columns(num_cols_app, gap='small')
    for index, option in enumerate(options):
        color = CARD_COLORS[index % len(CARD_COLORS)]
        with cols[index % num_cols_app]:
            if card(
                title=option["title"],
                text=option["text"],
                key=f"{selected_key}-{option['text']}",
                styles={
                    "card": {
                        "width": card_width,
                        "height": card_height,
                        "border-radius": "2px",
                        "background": color,
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": "2px solid #600000",
                        "text-align": "center",
                        "margin": "0px",
                    },
                    "text": {"font-family": "serif", "font-size": font_size_text},
                    "title": {"font-family": "serif", "font-size": font_size_title},},):
                if not st.session_state[f"{selected_key}_just_clicked"]:
                    st.session_state[selected_key] = option["text"]
                    st.session_state[f"{selected_key}_just_clicked"] = True
                    st.rerun() 
    st.session_state[f"{selected_key}_just_clicked"] = False


def student_tasks_page():
    if st.button("🔙 Menu"):
        st.session_state.student_action = None
        st.rerun()
    student_tool_page.main()
    
def student_chats_page():
    if st.button("🔙 Menu"):
        st.session_state.student_action = None
        st.rerun()
    contact_form.main()
   

def student_feedbback_page():
    if st.button("🔙 Menu"):
        st.session_state.student_action = None
        st.rerun()
    username = st.session_state.get('user_name')
    feed_back_button(supabase)
    view_feedback(username)
    
    
def show_resources_menu(page_title):
    if st.button("🔙 Home"):
        st.session_state.student_action = None
        st.rerun()
    resource_options = [
        {"title": '🧠', "text": "Challenges", "module": "cont"},
        {"title": "🛠️", "text": "Self-Help", "module": "help_tech"},
        {"title": "🎥", "text": "Videos", "module": "video_archives"},
        {"title": "🎧", "text": "Podcasts", "module": "podcasts"},
        # {"title": "📄", "text": "Articles", "module": "articles"},

        ]
    selected_key = "selected_resource"  
    selected_value = st.session_state.get(selected_key)
    if selected_value:
        selected_item = next((item for item in resource_options if item["text"] == selected_value), None)
        if selected_item:
            if st.button("🔙 Resources"):
                st.session_state[selected_key] = None
                st.rerun()
            set_full_page_background('images/black_strip.jpg')
            try:
                module = __import__(selected_item["module"])
                module.main()
            except Exception as e:
                st.info("🚧 This page is under development and its coming soon.")
            return
    display_card_menu(page_title, resource_options, selected_key=selected_key, num_cols=4)






class_list = ['','S1', 'S2', 'S3', 'S4', 'S5', 'S6']
stream_list = ['',"EAST", "SOUTH", 'WEST', 'NORTH']
gender_list = ['','MALE','FEMALE']



# ---------------- Utilities ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def edit_student_record(supabase: Client, user_id: str, new_age=None, username=None, password=None,
                        email=None, contact=None, new_class=None, new_stream=None):
    """
    Update student record in Supabase
    """
    try:
        update_data = {}
        if new_age is not None:
            update_data["age"] = new_age
        if username:
            update_data["username"] = username
        if password:
            update_data["password_hash"] = hash_password(password)
        if email:
            update_data["email"] = email
        if contact:
            update_data["contact"] = contact
        if new_class:
            update_data["class"] = new_class
        if new_stream:
            update_data["stream"] = new_stream

        update_data["last_update"] = datetime.now().isoformat()

        res = supabase.from_("users").update(update_data).eq("user_id", user_id).execute()

        if res.status_code >= 400:
            st.error(f"❌ Failed to update student record: {res.data}")
        else:
            st.success("✅ Student record updated successfully!")
            st.session_state.update_success = datetime.now().isoformat()

    except Exception as e:
        st.error(f"❌ Unexpected error updating student record: {e}")


def edit_student(supabase: Client, class_list, stream_list):
    if 'edit_student' not in st.session_state or not st.session_state.edit_student:
        return

    student = st.session_state.edit_student
    if 'show_password_fields' not in st.session_state:
        st.session_state.show_password_fields = False

    if st.button("Change Password"):
        st.session_state.show_password_fields = not st.session_state.show_password_fields
        st.rerun()

    with st.form('Edit Profile Form'):
        st.markdown("""
<div style="display:flex;align-items:center;gap:10px;">
  <div style="font-size:28px;padding:10px;border-radius:50%;background:#00897b;color:#fff;display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;">
    👤
  </div>
  <div>
    <div style="font-size:20px;font-weight:700;color:orange;">Edit Profile</div>
    <div style="font-size:12px;color:#586e75;">Update your account details below</div>
  </div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        username_input = col1.text_input(":orange[Username]", value=student['username'])
        email_input = col1.text_input(":orange[Email]", value=student.get('email', ''))
        contact_input = col2.text_input(":orange[Contact]", value=student.get('contact', ''))
        age_input = col2.number_input(":orange[AGE (yrs)]", value=student.get('age', 1), min_value=1, step=1)

        class_index = class_list.index(student.get('student_class')) if student.get('student_class') in class_list else 0
        class_input = col1.selectbox(":orange[CLASS]", class_list, index=class_index)

        stream_index = stream_list.index(student.get('stream')) if student.get('stream') in stream_list else 0
        stream_input = col2.selectbox(":orange[STREAM]", stream_list, index=stream_index)

        if st.session_state.show_password_fields:
            old_password_input = col1.text_input(":orange[Old Password]", type="password")
            new_password_input = col2.text_input(":orange[New Password]", type="password")
        else:
            old_password_input = None
            new_password_input = None

        update = st.form_submit_button(':orange[Update Profile]')

        if update:
            if st.session_state.show_password_fields:
                if not old_password_input or not new_password_input:
                    st.error("❌ Please enter both old and new passwords.")
                    return
                # Check old password
                hashed_old = hashlib.sha256(old_password_input.encode()).hexdigest()
                if hashed_old != student.get('password_hash'):
                    st.error("❌ Old password is incorrect. Please try again.")
                    return
            else:
                new_password_input = None
            edit_student_record(
                supabase,
                student['user_id'],
                new_age=age_input,
                username=username_input,
                password=new_password_input,
                email=email_input,
                contact=contact_input,
                new_class=class_input,
                new_stream=stream_input
            )

            # Update session state
            st.session_state.edit_student.update({
                'username': username_input,
                'email': email_input,
                'contact': contact_input,
                'age': age_input,
                'student_class': class_input,
                'stream': stream_input,
            })
            st.session_state.show_password_fields = False
            st.rerun()

    if st.session_state.get('update_success'):
        st.success(f"✅ Record updated at {st.session_state['update_success']}")
        del st.session_state['update_success']

def search_edit_and_update_student(supabase: Client, username: str, class_list, stream_list):
    if not username:
        return
    try:
        res = supabase.from_("users").select("*").eq("username", username).execute()
        if res.data:
            student = res.data[0]
            student_dict = {
                'user_id': student.get("user_id"),
                'name': student.get("full_name"),
                'age': student.get("age"),
                'student_class': student.get("class"),
                'stream': student.get("stream"),
                'username': student.get("username"),
                'email': student.get("email"),
                'contact': student.get("contact"),
                'password_hash': student.get("password_hash")
            }
            st.session_state.edit_student = student_dict
            # Pass class_list & stream_list to edit_student
            edit_student(supabase, class_list, stream_list)
        else:
            st.error("Student record not found in the database.")
    except Exception as e:
        st.error(f"⚠️ Unexpected error fetching student: {e}")


def display_student_profile(username, is_mobile: bool, supabase: Client):
    if not username:
        return

    st_details = fetch_student_details_by_username(username, supabase)
    st_details.pop("password_hash", None)  # remove sensitive field

    def format_line(label, value):
        return f"""
        <div style='margin-bottom:6px;'>
            <span style='color:#c0392b; font-weight:bold;'>{label}:</span>
            <span style='color:#27ae60;'>{value}</span>
        </div>
        """

    profile_html = ""
    profile_fields = [
        ("User ID", st_details.get("user_id") or "-"),
        ("Name", st_details.get("full_name") or "-"),
        ("Gender", st_details.get("sex") or "-"),
        ("Age", f"{st_details.get('age', '-')}" + (" Years" if st_details.get('age') else "")),
        ("Class", st_details.get("class") or "-"),
        ("Stream", st_details.get("stream") or "-"),
        ("Contact", st_details.get("contact") or "-"),
        ("Username", st_details.get("username") or "-"),
        ("Email", st_details.get("email") or "-"),
        ("Role", st_details.get("role") or "-"),
        ("Registered On", st_details.get("registration_date") or "Not available"),
        ("Last Update", st_details.get("last_update") or "Not available") ]

    for label, value in profile_fields:
        profile_html += format_line(label, value)
    if is_mobile:
        with st.expander("STUDENT PROFILE", expanded=False):
            st.markdown(profile_html, unsafe_allow_html=True)
    else:
        with st.sidebar.expander("STUDENT PROFILE", expanded=True):
            st.markdown(profile_html, unsafe_allow_html=True)

def profile_update(supabase: Client, username: str, is_mobile: bool, class_list, stream_list):
    if "show_profile_form" not in st.session_state:
        st.session_state.show_profile_form = False

    st.markdown("""
    <style>
    .top-right-button {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
    div.stButton > button {
        background-color: red;
        color: white !important;
        padding: 12px 28px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: green;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="top-right-button">', unsafe_allow_html=True)
    if not is_mobile:
        if st.sidebar.button("👤 EDIT PROFILE"):
            st.session_state.show_profile_form = not st.session_state.show_profile_form
    else:
        if st.button("👤 EDIT PROFILE"):
            st.session_state.show_profile_form = not st.session_state.show_profile_form
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_profile_form:
        set_full_page_background('images/black_strip.jpg')
        # Use Supabase version of search + edit
        search_edit_and_update_student(supabase, username, class_list, stream_list)
        if st.button("Close Profile"):
            st.session_state.show_profile_form = False
            time.sleep(1)
            st.rerun()





# ---------------- Save Feedback ----------------
def save_feedback(supabase: Client, message: str, username: str = "Anonymous"):
    """
    Save a feedback message to Supabase.
    """
    try:
        res = supabase.from_("feedbacks").insert([{
            "username": username,
            "message": message,
            "created_at": datetime.utcnow().isoformat()
        }]).execute()

        if hasattr(res, "status_code") and res.status_code >= 400:
            st.warning(f"⚠️ Could not save feedback: {res.data}")
            return False

        st.success("✅ Feedback submitted successfully!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Unexpected error saving feedback: {e}")
        return False

# ---------------- Get Full Name ----------------
def get_full_name_from_username(supabase: Client, username: str):
    """
    Fetch full_name from Supabase users table by username.
    """
    try:
        res = supabase.from_("users").select("full_name").eq("username", username).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("full_name")
        return username  # fallback
    except Exception as e:
        st.warning(f"⚠️ Unexpected error fetching full name: {e}")
        return username

# ---------------- Feedback Dialog ----------------
@st.dialog("💬 Give us Feedback", width='small')
def feedback_dialog(supabase: Client):
    username = st.session_state.get('user_name')
    st.write(username)
    name = get_full_name_from_username(supabase, username)

    st.markdown(f'## :green[Dear] :orange[{name}] !!')
    st.markdown("""
        <h4 style='color:skyblue;font-size:25px;'>We're here to listen.</h4>
        <p style='font-size:20px;'>Your thoughts help build a better mental health experience for everyone.</p>
    """, unsafe_allow_html=True)

    feedback = st.text_area("", height=200, placeholder="I feel...")

    if st.button("✅ Submit"):
        if feedback.strip():
            if save_feedback(supabase, feedback.strip(), username):
                time.sleep(1.5)
                st.rerun()
        else:
            st.warning("⚠️ Please enter your thoughts before submitting.")

# ---------------- Feedback Button ----------------
def feed_back_button(supabase: Client):
    if "show_feedback_form" not in st.session_state:
        st.session_state.show_feedback_form = False

    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #00897b;
            color: white !important;
            padding: 12px 28px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #e53935;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🗓️ Give us your feedback"):
        feedback_dialog(supabase)

# def view_feedback(supabase: Client, username: str = None):
#     try:
#         if username:
#             query = (
#                 supabase.from_("feedbacks")
#                 .select("id, message, created_at, responded_at, response, responder, users!inner(username)")
#                 .eq("users.username", username)
#                 .order("created_at", desc=True)
#             )
#         else:
#             query = (
#                 supabase.from_("feedbacks")
#                 .select("id, feedback, created_at, responded_at, response, responder, users(username)")
#                 .order("created_at", desc=True)
#             )

#         res = query.execute()

#         if not res.data:
#             st.info("No feedback found for this user.")
#             return

#         df = pd.DataFrame(res.data)
#         df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime('%Y-%m-%d %H:%M')
#         df["responded_at"] = pd.to_datetime(df.get("responded_at"), errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
#         df["responded_at"] = df["responded_at"].fillna('—')
#         df["response"] = df["response"].fillna('—')
#         df["responder"] = df["responder"].fillna('—')
#         df.index = df.index + 1

#         # Render table as before
#         st.markdown("""
#             <style>
#                 .feedback-table {border-collapse: collapse; width: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; color: #eee;}
#                 .feedback-table th, .feedback-table td {border: 1px solid #444; padding: 12px 15px; text-align: left;}
#                 .feedback-table th {background-color: #4A90E2; color: white; font-weight: 600;}
#                 .feedback-table tbody tr:nth-child(even) {background-color: #1e1e1e;}
#                 .feedback-table tbody tr:nth-child(odd) {background-color: #2c2c2c;}
#                 .message-cell {color: #8BC34A; font-weight: 600;}
#                 .response-cell {color: #2196F3; font-style: italic;}
#                 .meta-cell {color: #bbbbbb; font-size: 13px;}
#             </style>
#         """, unsafe_allow_html=True)

#         table_html = '<table class="feedback-table">'
#         table_html += "<thead><tr><th>#</th><th>Message</th><th>Sent_on</th><th>Reply</th><th>Reply date</th><th>Replied_by</th></tr></thead><tbody>"

#         for idx, row in df.iterrows():
#             table_html += f"""
#                 <tr>
#                     <td>{idx}</td>
#                     <td class="message-cell">{row['feedback']}</td>
#                     <td class="meta-cell">{row['created_at']}</td>
#                     <td class="response-cell">{row['response']}</td>
#                     <td class="meta-cell">{row['responded_at']}</td>
#                     <td class="meta-cell">{row['responder']}</td>
#                 </tr>
#             """
#         table_html += "</tbody></table>"
#         st.markdown(table_html, unsafe_allow_html=True)

#     except Exception as e:
#         st.error(f"⚠️ Unexpected error fetching feedback: {e}")

# ---------------- Save Feedback ----------------
def save_feedback(supabase: Client, message: str) -> bool:
    """
    Save a feedback message to Supabase for the logged-in user.
    """
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("❌ Could not identify user.")
        return False

    try:
        res = supabase.from_("feedbacks").insert([{
            "user_id": user_id,
            "message": message,
            "created_at": datetime.utcnow().isoformat()
        }]).execute()

        if hasattr(res, "status_code") and res.status_code >= 400:
            st.warning(f"⚠️ Could not save feedback: {res.data}")
            return False

        st.success("✅ Feedback submitted successfully!")
        return True

    except Exception as e:
        st.warning(f"⚠️ Unexpected error saving feedback: {e}")
        return False

# ---------------- Feedback Dialog ----------------
@st.dialog("💬 Give us Feedback", width='small')
def feedback_dialog(supabase: Client):
    name = st.session_state.get("name", "Anonymous")

    st.markdown(f'## :green[Dear] :orange[{name}] !!')
    st.markdown("""
        <h4 style='color:skyblue;font-size:25px;'>We're here to listen.</h4>
        <p style='font-size:20px;'>Your thoughts help build a better mental health experience for everyone.</p>
    """, unsafe_allow_html=True)

    feedback = st.text_area("", height=200, placeholder="I feel...")

    if st.button("✅ Submit"):
        if feedback.strip():
            if save_feedback(supabase, feedback.strip()):
                time.sleep(1.5)
                st.rerun()
        else:
            st.warning("⚠️ Please enter your thoughts before submitting.")

# ---------------- Feedback Button ----------------
def feed_back_button(supabase: Client):
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #00897b;
            color: white !important;
            padding: 12px 28px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #e53935;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🗓️ Give us your feedback"):
        feedback_dialog(supabase)

# ---------------- View Feedback ----------------
def view_feedback(supabase: Client):
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("❌ Could not identify user.")
        return

    try:
        res = supabase.from_("feedbacks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        if not res.data:
            st.info("No feedback found for this user.")
            return

        df = pd.DataFrame(res.data)
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime('%Y-%m-%d %H:%M')
        df["responded_at"] = pd.to_datetime(df.get("responded_at"), errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
        df["responded_at"] = df["responded_at"].fillna('—')
        df["response"] = df["response"].fillna('—')
        df["responder"] = df["responder"].fillna('—')
        df.index = df.index + 1

        st.markdown("""
            <style>
                .feedback-table {border-collapse: collapse; width: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; color: #eee;}
                .feedback-table th, .feedback-table td {border: 1px solid #444; padding: 12px 15px; text-align: left;}
                .feedback-table th {background-color: #4A90E2; color: white; font-weight: 600;}
                .feedback-table tbody tr:nth-child(even) {background-color: #1e1e1e;}
                .feedback-table tbody tr:nth-child(odd) {background-color: #2c2c2c;}
                .message-cell {color: #8BC34A; font-weight: 600;}
                .response-cell {color: #2196F3; font-style: italic;}
                .meta-cell {color: #bbbbbb; font-size: 13px;}
            </style>
        """, unsafe_allow_html=True)

        table_html = '<table class="feedback-table">'
        table_html += "<thead><tr><th>#</th><th>Message</th><th>Sent_on</th><th>Reply</th><th>Reply date</th><th>Replied_by</th></tr></thead><tbody>"

        for idx, row in df.iterrows():
            table_html += f"""
                <tr>
                    <td>{idx}</td>
                    <td class="message-cell">{row['message']}</td>
                    <td class="meta-cell">{row['created_at']}</td>
                    <td class="response-cell">{row['response']}</td>
                    <td class="meta-cell">{row['responded_at']}</td>
                    <td class="meta-cell">{row['responder']}</td>
                </tr>
            """
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Unexpected error fetching feedback: {e}")





def main():
    set_full_page_background('images/psy4.jpg')
    device_width = st_javascript("window.innerWidth", key="menu_device_width")
    username = st.session_state.get("user_name")
    if device_width is None:
        st.stop()
    is_mobile = device_width < 704

    # ---------------- Supabase Client ----------------
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    if username:
        st_details = fetch_student_details_by_username(username, supabase)
        st.session_state.student_id = st_details.get("user_id")
        st.session_state.name = st_details.get("full_name")
        st.session_state.student_class = st_details.get("class")
        st.session_state.stream = st_details.get("stream")
        st.session_state.gender = st_details.get("sex")
        st.session_state.contact = st_details.get("contact")

    # Display profile using Supabase
    display_student_profile(username, is_mobile, supabase)

    # Profile update should also use Supabase
    profile_update(supabase, username, is_mobile, class_list, stream_list)

    action = st.session_state.get("student_action")
    if action == "tasks":
        student_tasks_page()
    elif action == "find help":
        student_chats_page()
    elif action == "resources":
        show_resources_menu("📚 Student Resource Center")
    elif action == 'feedback':
        student_feedbback_page()
    else:
        student_menu()


if __name__ == "__main__":
    main()
