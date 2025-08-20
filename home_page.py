import streamlit as st
st.set_page_config(layout='wide')
from PIL import Image
from streamlit_option_menu import option_menu
import os, base64
import auth 
import bcrypt
import time
from PIL import Image
import os, base64
import pandas as pd
from streamlit_navigation_bar import st_navbar
from streamlit_javascript import st_javascript
from streamlit_option_menu import option_menu
from datetime import datetime
import teachers_page


from db_connection import supabase, get_admin_client
def get_device_type(width):
    if width is None:
        return "desktop"
    return "mobile" if width < 704 else "desktop"

screen_width = st_javascript("window.innerWidth", key="get_width")
device_type = get_device_type(screen_width)


if 'page' not in st.session_state:
    st.session_state.page = 'Home'

pages_desktop = ["🏠 Home", "🛠 Services", "👤 Account", "❓ Help"]
pages_mobile = ["Home", "Services", "Account", "Help"]
icons = ["house", "tools", "person", "question-circle"]

menu = None  
if device_type == "desktop":
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2.3rem; /* ⬅️ Changed from 2rem to 0rem */
    }
    header {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)
    base_styles = {
        "nav": {
            "background-color": "#1b4f72",
            "padding": "0.1rem 0.5rem",
            "box-shadow": "0 6px 10px rgba(0,0,0,0.15)",
            "font-size": "28px",
            "justify-content": "center",
            "flex-direction": "row",
            "display": "flex",
            "align-items": "center"
        },
        "span": {
            "display": "inline-block",
            "color": "white",
            "font-size": "20px",
            "font-weight": "bold",
            "padding": "0.7rem 1.2rem",
            "border-radius": "0.5rem",
            "transition": "all 0.3s ease",
        },
        "active": {"background-color": "green"},
        "hover": {"background-color": "red"},
    }

    menu = st_navbar(pages_desktop, styles=base_styles, key="main_navbar", options={"use_padding": False})
    menu = menu.replace("🏠 ", "").replace("🛠 ", "").replace("👤 ", "").replace("❓ ", "")
else:
    menu = option_menu(
        menu_title=None,
        options=pages_mobile,
        icons=icons,
        orientation="horizontal",
        default_index=0,
        styles={
            "container": {"background-color": "#1b4f72", "padding": "0.5rem"},
            "nav-link": {"font-size": "16px", "color": "white", "padding": "10px"},
            "nav-link-selected": {"background-color": "green"},
        },
    )
# ---------- Dark theme CSS ----------
dark_css = """
<style>
/* Only apply dark background where no custom background is set */
.stApp:not(.custom-background) {
    background-color: #121212 !important;
    color: #FFFFFF !important;
}

/* Inputs, buttons */
input, textarea, select, button, .stButton button {
    background-color: brown;
    color: orange;
    border-color: #555555 !important;
}

/* Tables */
.stDataFrame, .stDataFrame td, .stDataFrame th {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
}

/* Custom cards and existing backgrounds remain intact */
.custom-card, .custom-background {
    background-color: unset !important;
    color: unset !important;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #1E1E1E;
}
::-webkit-scrollbar-thumb {
    background-color: #555555;
    border-radius: 10px;
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

def set_custom_background(bg_color="#121212", sidebar_img_path=None, sidebar_width="200px"):
    """Set page background color or sidebar image. Leaves custom backgrounds untouched."""
    sidebar_img_b64 = ""
    if sidebar_img_path:
        with open(sidebar_img_path, "rb") as f:
            sidebar_img_b64 = base64.b64encode(f.read()).decode()

    page_bg = f"""
    <style>
    /* Main page */
    .stApp:not(.custom-background) {{
        background-color: {bg_color} !important;
    }}

    /* Sidebar width adjustment */
    section[data-testid="stSidebar"] {{
        width: {sidebar_width} !important;
        min-width: {sidebar_width} !important;
    }}

    /* Sidebar image */
    [data-testid="stSidebar"] > div:first-child {{
        {"background-image: url('data:image/png;base64," + sidebar_img_b64 + "');" if sidebar_img_b64 else ""}
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-size: cover;
    }}

    /* Header transparent */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
        padding-top: 0px;
    }}

    [data-testid="stToolbar"] {{
        right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)



def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("images/IMG.webp")
img2 = get_img_as_base64('images/saved.jpg')

def footer():
    st.markdown("©PPPS - Uganda. All rights reserved.", unsafe_allow_html=True)

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



defaults = {
    "page": "login",
    "show_login": False,
    "show_signup": False,
    "logged_in": False,
    "user_name": "",
    "user_role": "",
    "admin_redirect": False,
    "notified": False}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


@st.dialog("🗓️ Book Appointment", width="small")
def show_appointment_dialog():
    import time

    st.markdown("""
        <style>
        .tight-label {
            color: #FF8C00;
            font-weight: 500;
            margin: 0;
            padding: 0;
            line-height: 1;
            display: block;
            font-style: Times New Roman;
        }
        /* Pull inputs closer to labels */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input {
            margin-top: -5px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("appointment_form"):
        st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
        name = st.text_input("", key="appt_name")

        st.markdown('<span class="tight-label">Email Address</span>', unsafe_allow_html=True)
        email = st.text_input("", key="appt_email")

        st.markdown('<span class="tight-label">Telephone</span>', unsafe_allow_html=True)
        tel = st.text_input("", key="appt_tel", placeholder='')

        st.markdown('<span class="tight-label">Preferred Date</span>', unsafe_allow_html=True)
        date = st.date_input("")

        st.markdown('<span class="tight-label">Preferred Time</span>', unsafe_allow_html=True)
        time_input = st.time_input("")

        st.markdown('<span class="tight-label">Reason for Appointment</span>', unsafe_allow_html=True)
        reason = st.text_area("", height=100, key="appt_reason")

        submitted = st.form_submit_button("✅ Submit Appointment")

        if submitted:
            if name.strip() and email.strip() and reason.strip():
                st.success(f"✅ Appointment booked for {name} on {date} at {time_input}")
                time.sleep(2)
            else:
                st.warning("⚠️ Please fill in all required fields.")


def get_first_name_from_username(username):
    res = supabase.table("users").select("first_name").eq("username", username).execute()
    if res.data and res.data[0].get("first_name"):
        return res.data[0]["first_name"]
    return username

# ---------------- Session Event ----------------
def insert_session_event(user_id, role, name, event_type, session_duration=None):
    """Insert login/logout event into Supabase sessions table."""
    try:
        res = supabase.table("sessions").insert({
            "user_id": user_id,
            "role": role,
            "name": name,
            "event_type": event_type,
            "session_duration": session_duration,
            "timestamp": str(datetime.now())
        }).execute()

        if res.status_code >= 400:
            st.warning(f"⚠️ Could not insert session event: {res.data}")
            return False
        return True
    except Exception as e:
        st.warning(f"⚠️ Unexpected error inserting session event: {e}")
        return False


# ---------------- Helpers ----------------
def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins} minutes {secs} seconds"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours} hours {mins} minutes"

def parse_timestamp(ts):
    """Parse timestamp with or without microseconds."""
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")


# ---------------- Logout Flow ----------------
def logout():
    username = st.session_state.get("user_name")
    if username:
        try:
            res = supabase.table("users").select("user_id", "role", "full_name").eq("username", username).single().execute()
            user = res.data
            if user:
                user_id = user["user_id"]
                name = user["full_name"]
                role = user["role"]

                # Fetch last login timestamp
                login_res = supabase.table("sessions").select("timestamp").eq("user_id", user_id).eq("event_type", "login").order("timestamp", desc=True).limit(1).execute()
                login_row = login_res.data[0] if login_res.data else None

                if login_row:
                    login_time = parse_timestamp(login_row["timestamp"])
                    logout_time = datetime.now()
                    duration_sec = int((logout_time - login_time).total_seconds())
                    readable_duration = format_duration(duration_sec)
                    insert_session_event(user_id, role, name, 'logout', readable_duration)

        except Exception as e:
            st.warning(f"⚠️ Logout error: {e}")

    # Clear session state
    for key in ["logged_in", "user_name", "user_role", "show_login", "admin_redirect", "notified"]:
        st.session_state.pop(key, None)
    st.success("👋 Logged out successfully.")
    st.rerun()


# ---------------- Feedback ----------------
def save_feedback_supabase(message, name="Anonymous"):
    try:
        supabase.table("feedbacks").insert({
            "name": name,
            "message": message,
            "sent_at": str(datetime.now())
        }).execute()
        st.success("✅ Thank you for your feedback!")
    except Exception as e:
        st.error(f"⚠️ Could not save feedback: {e}")

# ---------------- Utilities ----------------
def get_fisrt_name_from_username(username: str) -> str:
    """
    Fetches the first_name of a user from Supabase using their username.
    Returns the first_name or username if not found.
    """
    try:
        res = supabase.from_("users").select("first_name").eq("username", username).execute()
        if hasattr(res, "status_code") and res.status_code >= 400:
            return username  # fallback
        data = getattr(res, "data", [])
        if data and "first_name" in data[0] and data[0]["first_name"]:
            return data[0]["first_name"]
        return username
    except Exception as e:
        print(f"⚠️ Error fetching first name: {e}")
        return username


@st.dialog("💬 Feedback")
def feedback_dialog():
    st.markdown("""
        <h4 style='color:skyblue;font-size:25px;'>We're here to listen.</h4>
        <p style='font-size:20px;'>Your thoughts help build a better mental health experience for everyone.</p>
    """, unsafe_allow_html=True)

    name = 'Anonymous'
    feedback = st.text_area("Your Message:", height=200, placeholder="I feel...")

    submitted = st.button("✅ Submit")
    if submitted:
        if feedback.strip():
            save_feedback_supabase(message=feedback.strip(), name=name)
            st.success("✅ Thank you for your feedback 💚")
            # optional delay for UX
            time.sleep(1.5)
            # reset dialog state without force rerun
            st.session_state.feedback_submitted = True
        else:
            st.warning("⚠️ Please enter your thoughts before submitting.")



# ---------------- Appointments ----------------
def save_appointment_supabase(name, email, tel, date, time_input, reason):
    try:
        supabase.table("online_appointments").insert({
            "name": name,
            "email": email,
            "tel": tel,
            "date": str(date),
            "time": str(time_input),
            "reason": reason,
            "requested_at": str(datetime.now())
        }).execute()
        st.success(f"✅ Appointment booked for {name} on {date} at {time_input}")
    except Exception as e:
        st.error(f"⚠️ Could not save appointment: {e}")


def view_appointments():
    try:
        res = supabase.table("online_appointments").select("*").order("requested_at", desc=True).execute()
        data = res.data if res.data else []
        df = pd.DataFrame(data)
        st.subheader("📅 Online Appointments")
        st.dataframe(df)
    except Exception as e:
        st.error(f"⚠️ Could not fetch appointments: {e}")





# def main():
#     set_full_page_background('images/dark_green_back.jpg')
#     st.markdown("""
#     <style>
#     [data-testid="stForm"] label {
#         color: white !important;
#         font-weight: 800 !important;
#         font-size: 50px !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

#     # auth.create_users_db() 
#     if st.session_state.get("logged_in"):
#         set_custom_background(bg_color="#121212", sidebar_img_path='images/IMG.webp', sidebar_width="350px")
        
#         # Corrected function name
#         first_name = get_first_name_from_username(st.session_state.user_name)
#         st.sidebar.success(f"👋 Welcome, {first_name}")

#         # Fetch user info from Supabase instead of SQLite
#         try:
#             res = supabase.from_("users").select("is_active").eq("username", st.session_state.user_name).execute()
#             if hasattr(res, "status_code") and res.status_code >= 400:
#                 st.warning(f"⚠️ Could not fetch user info: {getattr(res, 'data', res)}")
#                 return
#             user = res.data[0] if res.data else None
#         except Exception as e:
#             st.warning(f"⚠️ Unexpected error fetching user info: {e}")
#             return

#     if user and user.get("is_active") == 0:
#         st.warning("🚫 Your account has been deactivated. Please contact admin.")
#         for key in ["logged_in", "user_name", "user_role", "show_login", "admin_redirect"]:
#             st.session_state[key] = False if isinstance(st.session_state.get(key), bool) else ""
#         return
def main():
    set_full_page_background('images/dark_green_back.jpg')
    st.markdown("""
    <style>
    [data-testid="stForm"] label {
        color: white !important;
        font-weight: 800 !important;
        font-size: 50px !important;
    }
    </style>
""", unsafe_allow_html=True)

    user = None  # 👈 Initialize here

    if st.session_state.get("logged_in"):
        set_custom_background(bg_color="#121212", sidebar_img_path='images/IMG.webp', sidebar_width="350px")
        
        # Corrected function name
        first_name = get_first_name_from_username(st.session_state.user_name)
        st.sidebar.success(f"👋 Welcome, {first_name}")

        # Fetch user info from Supabase
        try:
            res = supabase.from_("users").select("is_active").eq("username", st.session_state.user_name).execute()
            if hasattr(res, "status_code") and res.status_code >= 400:
                st.warning(f"⚠️ Could not fetch user info: {getattr(res, 'data', res)}")
                return
            user = res.data[0] if res.data else None
        except Exception as e:
            st.warning(f"⚠️ Unexpected error fetching user info: {e}")
            return

    # Now safe to check
    if user and user.get("is_active") == 0:
        st.warning("🚫 Your account has been deactivated. Please contact admin.")
        for key in ["logged_in", "user_name", "user_role", "show_login", "admin_redirect"]:
            st.session_state[key] = False if isinstance(st.session_state.get(key), bool) else ""
        return

    if menu.endswith("Home"):
        import welcome
        welcome.main()       
        if "show_appointment_form" not in st.session_state:
            st.session_state.show_appointment_form = False

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

        if st.button("🗓️ Book Appointment"):
            st.session_state.show_appointment_dialog = True

        if st.session_state.get("show_appointment_dialog", False):

            @st.dialog("🗓️ Book Appointment", width="small")
            def show_appointment_dialog():
                st.markdown("""
                    <style>
                    .tight-label {
                        color: #FF8C00;
                        font-weight: 500;
                        margin: 0;
                        padding: 0;
                        line-height: 1;
                        display: block;
                        font-style: Times New Roman;
                    }
                    .stTextInput > div > div > input,
                    .stTextArea > div > div > textarea,
                    .stDateInput > div > div > input,
                    .stTimeInput > div > div > input {
                        margin-top: -5px !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                with st.form("appointment_form"):
                    st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
                    name = st.text_input("", key="appt_name")

                    st.markdown('<span class="tight-label">Email Address</span>', unsafe_allow_html=True)
                    email = st.text_input("", key="appt_email")

                    st.markdown('<span class="tight-label">Telephone</span>', unsafe_allow_html=True)
                    tel = st.text_input("", key="appt_tel", placeholder='')

                    st.markdown('<span class="tight-label">Preferred Date</span>', unsafe_allow_html=True)
                    date = st.date_input("")

                    st.markdown('<span class="tight-label">Preferred Time</span>', unsafe_allow_html=True)
                    time_input = st.time_input("")

                    st.markdown('<span class="tight-label">Reason for Appointment</span>', unsafe_allow_html=True)
                    reason = st.text_area("", height=100, key="appt_reason")

                    submitted = st.form_submit_button("✅ Submit Appointment")
                    if submitted:
                        if name.strip() and email.strip() and reason.strip():
                            save_appointment_supabase(name, email, tel, date, time_input, reason)
                            st.session_state.show_appointment_form = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("⚠️ Please fill in all required fields.")
            show_appointment_dialog()

        # ---------------- Columns ----------------
        col1, col2, col3 = st.columns([1.5, 1, 0.8], gap="small")

        with col3:
            st.markdown("""
            <div style="
                background-color: #f3f8fb;
                padding: 25px;
                border-radius: 20px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 320px;
            ">
                <div>
                    <h4 style="color:#1b4f72; margin-top: 0;">📞 <strong>Reach Out</strong></h4>
                    <p style="font-size: 18px; color:#333; margin-bottom: 15px;">
                        <span style="font-size: 14px;">📱</span> WhatsApp: <strong>0781 950 263</strong><br>
                        <span style="font-size: 18px;">☎️</span> Call: <strong>0200 804 010</strong><br>
                        <em>(Mon–Fri, 9 AM–6 PM)</em>
                    </p>
                </div>
                <div style="margin-top: 15px;">
                    <!-- The button will go here -->
                </div>
            </div>
            """, unsafe_allow_html=True)
            # import time
            # button_click()
        
        with col2:
            st.markdown("""
                <div style="
                    background-color: #f3f8fb;
                    padding: 25px;
                    border-radius: 20px;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
                    height: 320px;
                    text-align: center;
                ">
                    <h3 style="color:#1b4f72; margin-top: 0;">💬 <strong>Share Your Thoughts</strong></h3>
                    <p style="font-size: 20px; line-height: 1.6; color:#1b4f72;">
                        Your voice matters. Help us create a better, safer environment by sharing your anonymous feedback.<br>
                        We're here to listen <strong>every day from 9 AM to 6 PM</strong>.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Give Your Feedback"):
                
                st.session_state.show_feedback_dialog = True
            if st.session_state.get("show_feedback_dialog"):
                feedback_dialog()
                # optionally reset the state after closing the dialog
                if st.session_state.get("feedback_submitted"):
                    st.session_state.show_feedback_dialog = False
                    st.session_state.feedback_submitted = False


        with col1:
            st.markdown("""
            <div style="
                background-color: #f3f8fb;
                padding: 25px;
                border-radius: 20px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.05);
                height: 320px;
                overflow-y: auto;
            ">
                <h4 style="color:#1b4f72; margin-top: 0;">❓ <strong>Frequently Asked Questions</strong></h4>
                <details style="margin-top: 15px;">
                  <summary style="font-weight: bold; font-size: 20px; cursor: pointer; color:#1b4f72;">How do I know if my child needs mental health support?</summary>
                  <p style="margin-left: 15px; font-size: 18px; color:#444;">
                    Look for changes in mood, behavior, sleep, or appetite lasting more than two weeks. 
                    If you're worried, consult a counselor or healthcare professional for an evaluation.
                  </p>
                </details>
                <details style="margin-top: 10px;">
                  <summary style="font-weight: bold; font-size: 20px; cursor: pointer; color:#1b4f72;">What mental health resources are available for students at school?</summary>
                  <p style="margin-left: 15px; font-size: 18px; color:#444;">
                    Many schools offer counseling services, peer support groups, and mental health awareness programs. 
                    Reach out to your school counselor or health office for guidance.
                  </p>
                </details>
                <details style="margin-top: 10px;">
                  <summary style="font-weight: bold; font-size: 20px; cursor: pointer; color:#1b4f72;">How can teachers support students struggling with mental health?</summary>
                  <p style="margin-left: 15px; font-size: 18px; color:#444;">
                    Teachers can create a safe and supportive classroom environment, listen without judgment, 
                    and refer students to school counselors or mental health professionals when needed.
                  </p>
                </details>
                <details style="margin-top: 10px;">
                  <summary style="font-weight: bold; font-size: 20px; cursor: pointer; color:#1b4f72;">Is mental health support confidential?</summary>
                  <p style="margin-left: 15px; font-size: 18px; color:#444;">
                    Yes, professional mental health services respect your privacy and keep your information confidential 
                    unless there is a risk of harm to yourself or others.
                  </p>
                </details>
                <details style="margin-top: 10px;">
                  <summary style="font-weight: bold; font-size: 20px; cursor: pointer; color:#1b4f72;">How can I access emergency mental health help?</summary>
                  <p style="margin-left: 15px; font-size: 18px; color:#444;">
                    If you or someone you know is in crisis, call emergency services immediately or visit the nearest hospital emergency department.
                  </p>
                </details>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        

    elif menu.endswith("Services"):
        import cont
        cont.main()
    elif menu.endswith("Account"):
        if st.session_state.get("logged_in"):
            role = st.session_state.get("user_role")
            if role == "Admin":
                import admin
                admin.main()
            elif role == "Admin2":
                import super_admin
                super_admin.main()
            elif role == "Therapist":
                import therapist
                therapist.main()
            elif role == "Teacher":
                import teachers_page
                teachers_page.main()
            elif role == "Parent":
                import parents_page
                parents_page.main()
            elif role == "Student":
                import student_page
                student_page.main()
            with st.sidebar:
                if st.button("🚪 Logout"):
                    logout()

        else:
            import welcome
            welcome.main()
            if st.session_state.get("show_login"):
                auth.show_login_dialog()
            elif st.session_state.get("show_signup"):
                auth.show_signup_dialog()
            else:
                st.session_state.show_login = True
                st.rerun()
    elif menu.endswith("Help"):
        st.info("💬 How can we assist you?")
    st.write('---')
    footer()

if __name__ == "__main__":
    main()




