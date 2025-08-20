import streamlit as st
import sqlite3
import hashlib
import time
from pushbullet import Pushbullet
from datetime import datetime
from pathlib import Path
API_KEY = st.secrets["push_API_KEY"]
dark_css = """
<style>
/* ---------- DARK THEME ---------- */
.stApp.dark {
    background-color: #121212 !important;
    color: #FFFFFF !important;
}

/* Force input labels to show in both themes */
.stApp.dark [data-testid="stMarkdownContainer"],
.stApp.dark .stTextInput label,
.stApp.dark .stPasswordInput label,
.stApp.dark .stSelectbox label,
.stApp.dark legend {
    color: #FFFFFF;
}

.stApp:not(.dark) [data-testid="stMarkdownContainer"],
.stApp:not(.dark) .stTextInput label,
.stApp:not(.dark) .stPasswordInput label,
.stApp:not(.dark) .stSelectbox label,
.stApp:not(.dark) legend {
    color: #000000 !important;
}

/* Inputs, buttons (dark theme only) */
.stApp.dark input,
.stApp.dark textarea,
.stApp.dark select,
.stApp.dark button,
.stApp.dark .stButton button {
    background-color: #333333 !important;
    color: #FFFFFF !important;
    border-color: #555555 !important;
}

/* Tables */
.stApp.dark .stDataFrame,
.stApp.dark .stDataFrame td,
.stApp.dark .stDataFrame th {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
}

/* Preserve custom cards/backgrounds */
.custom-card, .custom-background {
    background-color: unset !important;
    color: unset !important;
}

/* Scrollbars (dark only) */
.stApp.dark ::-webkit-scrollbar {
    width: 10px;
}
.stApp.dark ::-webkit-scrollbar-track {
    background: #1E1E1E;
}
.stApp.dark ::-webkit-scrollbar-thumb {
    background-color: #555555;
    border-radius: 10px;
}
</style>
"""

# import streamlit as st
# from supabase import create_client, Client
# import hashlib
# from datetime import datetime
# import time

# # ---------------- Supabase ----------------
# SUPABASE_URL = st.secrets["supabase"]["url"]
# SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
# SUPABASE_SERVICE_KEY = st.secrets["supabase"]["service_role_key"]
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# # ---------------- Utilities ----------------
# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode()).hexdigest()

# def verify_password(password: str, hashed: str) -> bool:
#     return hashlib.sha256(password.encode()).hexdigest() == hashed



# def generate_user_id(role: str) -> str:
#     prefix_map = {
#         'student': 'STUD',
#         'parent': 'PARENT',
#         'teacher': 'TEACH',
#         'therapist': 'USER',
#         'admin': 'ADMIN'
#     }
#     prefix = prefix_map.get(role.lower(), 'GUEST')
#     today = datetime.now().strftime("%Y%m%d")

#     if "last_user_num" not in st.session_state:
#         st.session_state.last_user_num = {}

#     key = f"{prefix}-{today}"
#     start = st.session_state.last_user_num.get(key, 0) + 1

#     for attempt in range(start, 10000):  # max 9999 users per day
#         user_id = f"{prefix}-{today}-{attempt:04d}"
#         try:
#             res = supabase.from_("users").select("user_id").eq("user_id", user_id).execute()
#             if res.status_code >= 400:
#                 print("Supabase error fetching user_id:", res.data)
#                 break  # stop trying if Supabase fails
#             if not res.data:  # ID is free
#                 st.session_state.last_user_num[key] = attempt
#                 return user_id
#         except Exception as e:
#             print("Supabase exception:", e)
#             break

#     # fallback
#     return f"{prefix}-{today}-0001"


# def insert_user(data: dict):
#     try:
#         res = supabase.from_("users").insert(data).execute()

#         # ✅ v2 compatible: check status_code instead of .error
#         if res.status_code >= 400:
#             return False, f"🚫 Supabase error: {res.data}"
        
#         return True, "✅ User registered successfully!"
    
#     except Exception as e:
#         return False, f"⚠️ Unexpected error: {e}"

# def authenticate_user(username: str, password: str):
#     res = supabase.from_("users").select("*").eq("username", username).execute()
#     users = res.data
#     if not users:
#         return False, username, None
#     user = users[0]
#     if verify_password(password, user["password_hash"]):
#         if not user.get("is_active", True):
#             return False, username, None
#         return True, user["username"], user["role"]
#     return False, username, None

# def insert_session_event(user_id, role, name, event_type, session_duration=None):
#     try:
#         res = supabase.from_("sessions").insert({
#             "user_id": user_id,
#             "role": role,
#             "name": name,
#             "event_type": event_type,
#             "session_duration": session_duration,
#             "timestamp": datetime.now().isoformat()
#         }).execute()

#         if res.status_code >= 400:
#             st.warning(f"⚠️ Could not insert session event: {res.data}")
#             return False
#         return True
#     except Exception as e:
#         st.warning(f"⚠️ Unexpected error inserting session event: {e}")
#         return False


# # ---------------- Login Dialog ----------------
# @st.dialog("🔐 Sign In", width='small')
# def show_login_dialog():
#     st.markdown("""
#         <style>
#         .tight-label { color: #1E90FF; font-weight: 250; padding:0; margin:0; line-height:0.5; display:block; font-style:Times New Roman; }
#         .stTextInput > div > div > input { margin-top: -5px !important; }
#         </style>
#     """, unsafe_allow_html=True)

#     with st.form("login_form"):
#         st.markdown('<span class="tight-label">Username</span>', unsafe_allow_html=True)
#         username_input = st.text_input("", key="login_username")
#         st.markdown('<span class="tight-label">Password</span>', unsafe_allow_html=True)
#         password_input = st.text_input("", type="password", key="login_password")
#         submitted = st.form_submit_button(":green[Login]")

#         if submitted:
#             success, username, role = authenticate_user(username_input, password_input)
#             if success:
#                 st.session_state.logged_in = True
#                 st.session_state.user_name = username
#                 st.session_state.user_role = role
#                 st.session_state.show_login = False
#                 st.success(f"🎉 Welcome {username}!")
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid username or password.")

#     col1, col2 = st.columns([3, 2])
#     with col1:
#         st.markdown(":orange[Don't have an account yet?]")
#     with col2:
#         if st.button(":green[👉 Create yours here]", key="to_signup"):
#             st.session_state.show_login = False
#             st.session_state.show_signup = True
#             st.rerun()

# # ---------------- Signup Dialog ----------------
# @st.dialog("📝 Register here", width="small")
# def show_signup_dialog():
#     import time

#     st.markdown("""
#         <style>
#         .tight-label { color: #1E90FF; font-weight: 250; padding:0; margin:0; line-height:0.5; display:block; font-style:Times New Roman; }
#         .stTextInput > div > div > input,
#         .stNumberInput > div > div > input,
#         .stTextArea > div > div > textarea,
#         .stSelectbox > div > div > div { margin-top:-5px !important; }
#         </style>
#     """, unsafe_allow_html=True)

#     st.markdown('<span class="tight-label">Select Role</span>', unsafe_allow_html=True)
#     role = st.selectbox("", ["Select role ..","Student","Parent","Teacher","Therapist","Admin","Admin2"])

#     if role != "Select role ..":
#         with st.form("signup_form"):
#             # Initialize all fields
#             first_name = last_name = full_name = username = email = password = confirm_password = None
#             sex = age = class_ = stream = parent_guardian = profession = address = contact = None

#             # --- Role-dependent fields ---
#             if role == "Student":
#                 st.markdown('<span class="tight-label">First Name</span>', unsafe_allow_html=True)
#                 first_name = st.text_input("", key="first_name")
#                 st.markdown('<span class="tight-label">Last Name</span>', unsafe_allow_html=True)
#                 last_name = st.text_input("", key="last_name")
#                 full_name = f"{first_name.strip()} {last_name.strip()}" if first_name and last_name else None

#                 st.markdown('<span class="tight-label">Sex</span>', unsafe_allow_html=True)
#                 sex = st.selectbox("", ["Male", "Female", "Other"])
#                 st.markdown('<span class="tight-label">Age</span>', unsafe_allow_html=True)
#                 age = st.number_input("", 3, 100, step=1)

#                 st.markdown('<span class="tight-label">Parent/Guardian</span>', unsafe_allow_html=True)
#                 parent_guardian = st.text_input("", key="parent_guardian")
#                 st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
#                 address = st.text_area("", key="address")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#                 # --- Fetch Class & Stream dynamically ---
#                 try:
#                     class_res = supabase.from_("class_options").select("name").execute()
#                     stream_res = supabase.from_("stream_options").select("name").execute()
#                     class_list = [r["name"] for r in class_res.data] if class_res.data else []
#                     stream_list = [r["name"] for r in stream_res.data] if stream_res.data else []
#                 except Exception as e:
#                     st.warning(f"⚠️ Could not fetch Class/Stream: {e}")
#                     class_list, stream_list = [], []

#                 default_classes = ["S.1","S.2","S.3","S.4","S.5","S.6"]
#                 default_streams = ["EAST","WEST","NORTH","SOUTH"]

#                 class_list = default_classes + [c for c in class_list if c not in default_classes]
#                 stream_list = default_streams + [s for s in stream_list if s not in default_streams]

#                 st.markdown('<span class="tight-label">Class</span>', unsafe_allow_html=True)
#                 class_choice = st.selectbox("", class_list + ["Other"], key="class_select")
#                 class_ = st.text_input("Enter class", key="custom_class") if class_choice == "Other" else class_choice

#                 st.markdown('<span class="tight-label">Stream</span>', unsafe_allow_html=True)
#                 stream_choice = st.selectbox("", stream_list + ["Other"], key="stream_select")
#                 stream = st.text_input("Enter stream", key="custom_stream") if stream_choice == "Other" else stream_choice

#             elif role in ["Parent","Teacher"]:
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")
#                 st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
#                 address = st.text_area("", key="address")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#             elif role == "Therapist":
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")
#                 st.markdown('<span class="tight-label">Profession</span>', unsafe_allow_html=True)
#                 profession = st.text_input("", key="profession")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#             elif role in ["Admin","Admin2"]:
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")

#             # --- Common fields ---
#             st.markdown('<span class="tight-label">Username</span>', unsafe_allow_html=True)
#             username = st.text_input("", key="username")
#             st.markdown('<span class="tight-label">Email</span>', unsafe_allow_html=True)
#             email = st.text_input("", key="email")
#             st.markdown('<span class="tight-label">Password</span>', unsafe_allow_html=True)
#             password = st.text_input("", type="password", key="password")
#             st.markdown('<span class="tight-label">Confirm Password</span>', unsafe_allow_html=True)
#             confirm_password = st.text_input("", type="password", key="confirm_password")

#             submitted = st.form_submit_button(":green[Create Account]")

#             if submitted:
#                 if not username or not email or not password or not confirm_password or (role=="Student" and (not first_name or not last_name)):
#                     st.warning("⚠️ Please fill all required fields")
#                 elif password != confirm_password:
#                     st.warning("⚠️ Passwords do not match")
#                 else:
#                     user_id = generate_user_id(role)
#                     password_hash = hash_password(password)

#                     # --- Safe data payload ---
#                     data = {
#                         "user_id": user_id,
#                         "username": username,
#                         "password_hash": password_hash,
#                         "role": role,
#                         "email": email or None,
#                         "first_name": first_name or None,
#                         "last_name": last_name or None,
#                         "full_name": full_name or None,
#                         "sex": sex or None,
#                         "age": int(age) if age else None,
#                         "class": class_ or None,
#                         "stream": stream or None,
#                         "address": address or None,
#                         "parent_guardian": parent_guardian or None,
#                         "contact": contact or None,
#                         "profession": profession or None,
#                         "is_active": 1
#                     }

#                     success, msg = insert_user(data)

#                     if success:
#                         # Save new Class/Stream if custom
#                         try:
#                             if class_ and class_ not in default_classes:
#                                 supabase.from_("class_options").insert({"name": class_}).execute()
#                             if stream and stream not in default_streams:
#                                 supabase.from_("stream_options").insert({"name": stream}).execute()
#                         except Exception as e:
#                             st.warning(f"⚠️ Could not save custom class/stream: {e}")

#                         st.success(msg)
#                         time.sleep(2)
#                         st.session_state.show_signup = False
#                         st.session_state.show_login = True
#                         st.rerun()
#                     else:
#                         st.error(msg)

#         # Login link outside form
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             st.markdown(":orange[Already have an account?]")
#         with col2:
#             if st.button(":blue[👉 Go to Login]", key="to_login"):
#                 st.session_state.show_signup = False
#                 st.session_state.show_login = True
#                 st.rerun()
import streamlit as st
from supabase import create_client, Client
import hashlib
from datetime import datetime
import time

# ---------------- Supabase ----------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
SUPABASE_SERVICE_KEY = st.secrets["supabase"]["service_role_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------------- Utilities ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def generate_user_id(role: str) -> str:
    prefix_map = {
        'student': 'STUD',
        'parent': 'PARENT',
        'teacher': 'TEACH',
        'therapist': 'USER',
        'admin': 'ADMIN'
    }
    prefix = prefix_map.get(role.lower(), 'GUEST')
    today = datetime.now().strftime("%Y%m%d")

    key = f"{prefix}-{today}"

    # Start from last session number or 1
    start = st.session_state.get("last_user_num", {}).get(key, 1)

    for attempt in range(start, 10000):  # max 9999 users per day
        user_id = f"{prefix}-{today}-{attempt:04d}"
        try:
            res = supabase.from_("users").select("user_id").eq("user_id", user_id).execute()
            if res.error:
                # If Supabase fails, skip to fallback
                break
            if not res.data:  # ID is free
                # Save last used number in session state
                if "last_user_num" not in st.session_state:
                    st.session_state.last_user_num = {}
                st.session_state.last_user_num[key] = attempt
                return user_id
        except Exception as e:
            break

    # Fallback if all else fails
    attempt = int(datetime.now().timestamp()) % 10000
    return f"{prefix}-{today}-{attempt:04d}"

# def insert_user(data: dict):
#     try:
#         res = supabase.from_("users").insert(data).execute()
#         if res.error:
#             return False, f"🚫 Supabase error: {res.error.message}"
#         return True, "✅ User registered successfully!"
#     except Exception as e:
#         return False, f"⚠️ Unexpected error: {e}"
def insert_user(data: dict, max_retries=3):
    for _ in range(max_retries):
        try:
            res = supabase.from_("users").insert(data).execute()
            if res.error:
                if 'duplicate key' in res.error.message.lower():
                    # regenerate user_id and retry
                    data['user_id'] = generate_user_id(data['role'])
                    continue
                return False, f"🚫 Supabase error: {res.error.message}"
            return True, "✅ User registered successfully!"
        except Exception as e:
            return False, f"⚠️ Unexpected error: {e}"
    return False, "⚠️ Could not generate a unique user ID after several attempts."


def authenticate_user(username: str, password: str):
    try:
        res = supabase.from_("users").select("*").eq("username", username).execute()
        if res.error:
            st.warning(f"⚠️ Supabase error: {res.error.message}")
            return False, username, None
        users = res.data
        if not users:
            return False, username, None
        user = users[0]
        if verify_password(password, user["password_hash"]):
            if not user.get("is_active", True):
                return False, username, None
            return True, user["username"], user["role"]
        return False, username, None
    except Exception as e:
        st.warning(f"⚠️ Unexpected error: {e}")
        return False, username, None

# ---------------- Login Dialog ----------------
@st.dialog("🔐 Sign In", width='small')
def show_login_dialog():
    st.markdown("""
        <style>
        .tight-label { color: #1E90FF; font-weight: 250; padding:0; margin:0; line-height:0.5; display:block; font-style:Times New Roman; }
        .stTextInput > div > div > input { margin-top: -5px !important; }
        </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown('<span class="tight-label">Username</span>', unsafe_allow_html=True)
        username_input = st.text_input("", key="login_username")
        st.markdown('<span class="tight-label">Password</span>', unsafe_allow_html=True)
        password_input = st.text_input("", type="password", key="login_password")
        submitted = st.form_submit_button(":green[Login]")

        if submitted:
            success, username, role = authenticate_user(username_input, password_input)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_name = username
                st.session_state.user_role = role
                st.session_state.show_login = False
                st.success(f"🎉 Welcome {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(":orange[Don't have an account yet?]")
    with col2:
        if st.button(":green[👉 Create yours here]", key="to_signup"):
            st.session_state.show_login = False
            st.session_state.show_signup = True
            st.rerun()

# ---------------- Signup Dialog ----------------
# @st.dialog("📝 Register here", width="small")
# def show_signup_dialog():
#     st.markdown("""
#         <style>
#         .tight-label { color: #1E90FF; font-weight: 250; padding:0; margin:0; line-height:0.5; display:block; font-style:Times New Roman; }
#         .stTextInput > div > div > input,
#         .stNumberInput > div > div > input,
#         .stTextArea > div > div > textarea,
#         .stSelectbox > div > div > div { margin-top:-5px !important; }
#         </style>
#     """, unsafe_allow_html=True)

#     st.markdown('<span class="tight-label">Select Role</span>', unsafe_allow_html=True)
#     role = st.selectbox("", ["Select role ..","Student","Parent","Teacher","Therapist","Admin","Admin2"])

#     if role != "Select role ..":
#         with st.form("signup_form"):
#             # initialize fields
#             first_name = last_name = full_name = username = email = password = confirm_password = None
#             sex = age = class_ = stream = parent_guardian = profession = address = contact = None

#             # --- Role-dependent fields ---
#             if role == "Student":
#                 st.markdown('<span class="tight-label">First Name</span>', unsafe_allow_html=True)
#                 first_name = st.text_input("", key="first_name")
#                 st.markdown('<span class="tight-label">Last Name</span>', unsafe_allow_html=True)
#                 last_name = st.text_input("", key="last_name")
#                 full_name = f"{first_name.strip()} {last_name.strip()}" if first_name and last_name else None

#                 st.markdown('<span class="tight-label">Sex</span>', unsafe_allow_html=True)
#                 sex = st.selectbox("", ["Male", "Female", "Other"])
#                 st.markdown('<span class="tight-label">Age</span>', unsafe_allow_html=True)
#                 age = st.number_input("", 3, 100, step=1)
#                 st.markdown('<span class="tight-label">Parent/Guardian</span>', unsafe_allow_html=True)
#                 parent_guardian = st.text_input("", key="parent_guardian")
#                 st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
#                 address = st.text_area("", key="address")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#                 # --- Fetch Class & Stream safely ---
#                 try:
#                     class_res = supabase.from_("class_options").select("name").execute()
#                     stream_res = supabase.from_("stream_options").select("name").execute()
#                     class_list = [r["name"] for r in class_res.data] if class_res.data else []
#                     stream_list = [r["name"] for r in stream_res.data] if stream_res.data else []
#                 except Exception:
#                     class_list, stream_list = [], []

#                 default_classes = ["S.1","S.2","S.3","S.4","S.5","S.6"]
#                 default_streams = ["EAST","WEST","NORTH","SOUTH"]
#                 class_list = default_classes + [c for c in class_list if c not in default_classes]
#                 stream_list = default_streams + [s for s in stream_list if s not in default_streams]

#                 st.markdown('<span class="tight-label">Class</span>', unsafe_allow_html=True)
#                 class_choice = st.selectbox("", class_list + ["Other"], key="class_select")
#                 class_ = st.text_input("Enter class", key="custom_class") if class_choice == "Other" else class_choice

#                 st.markdown('<span class="tight-label">Stream</span>', unsafe_allow_html=True)
#                 stream_choice = st.selectbox("", stream_list + ["Other"], key="stream_select")
#                 stream = st.text_input("Enter stream", key="custom_stream") if stream_choice == "Other" else stream_choice

#             elif role in ["Parent","Teacher"]:
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")
#                 st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
#                 address = st.text_area("", key="address")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#             elif role == "Therapist":
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")
#                 st.markdown('<span class="tight-label">Profession</span>', unsafe_allow_html=True)
#                 profession = st.text_input("", key="profession")
#                 st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
#                 contact = st.text_input("", key="contact")

#             elif role in ["Admin","Admin2"]:
#                 st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
#                 full_name = st.text_input("", key="full_name")

#             # --- Common fields ---
#             st.markdown('<span class="tight-label">Username</span>', unsafe_allow_html=True)
#             username = st.text_input("", key="username")
#             st.markdown('<span class="tight-label">Email</span>', unsafe_allow_html=True)
#             email = st.text_input("", key="email")
#             st.markdown('<span class="tight-label">Password</span>', unsafe_allow_html=True)
#             password = st.text_input("", type="password", key="password")
#             st.markdown('<span class="tight-label">Confirm Password</span>', unsafe_allow_html=True)
#             confirm_password = st.text_input("", type="password", key="confirm_password")

#             submitted = st.form_submit_button(":green[Create Account]")

#             if submitted:
#                 if not username or not email or not password or not confirm_password or (role=="Student" and (not first_name or not last_name)):
#                     st.warning("⚠️ Please fill all required fields")
#                 elif password != confirm_password:
#                     st.warning("⚠️ Passwords do not match")
#                 else:
#                     user_id = generate_user_id(role)
#                     password_hash = hash_password(password)
#                     data = {
#                         "user_id": user_id,
#                         "username": username,
#                         "password_hash": password_hash,
#                         "role": role,
#                         "email": email or None,
#                         "first_name": first_name or None,
#                         "last_name": last_name or None,
#                         "full_name": full_name or None,
#                         "sex": sex or None,
#                         "age": int(age) if age else None,
#                         "class": class_ or None,
#                         "stream": stream or None,
#                         "address": address or None,
#                         "parent_guardian": parent_guardian or None,
#                         "contact": contact or None,
#                         "profession": profession or None,
#                         "is_active": 1
#                     }

#                     success, msg = insert_user(data)

#                     if success:
#                         # Save new Class/Stream if custom
#                         try:
#                             if class_ and class_ not in default_classes:
#                                 supabase.from_("class_options").insert({"name": class_}).execute()
#                             if stream and stream not in default_streams:
#                                 supabase.from_("stream_options").insert({"name": stream}).execute()
#                         except Exception as e:
#                             st.warning(f"⚠️ Could not save custom class/stream: {e}")

#                         st.success(msg)
#                         time.sleep(2)
#                         st.session_state.show_signup = False
#                         st.session_state.show_login = True
#                         st.rerun()
#                     else:
#                         st.error(msg)

#         # Login link outside form
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             st.markdown(":orange[Already have an account?]")
#         with col2:
#             if st.button(":blue[👉 Go to Login]", key="to_login"):
#                 st.session_state.show_signup = False
#                 st.session_state.show_login = True
#                 st.rerun()
# ---------------- Signup Dialog ----------------

# ---------------- Utilities ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def generate_user_id(role: str) -> str:
    prefix_map = {
        'student': 'STUD',
        'parent': 'PARENT',
        'teacher': 'TEACH',
        'therapist': 'USER',
        'admin': 'ADMIN'
    }
    prefix = prefix_map.get(role.lower(), 'GUEST')
    today = datetime.now().strftime("%Y%m%d")

    if "last_user_num" not in st.session_state:
        st.session_state.last_user_num = {}

    key = f"{prefix}-{today}"
    start = st.session_state.last_user_num.get(key, 0) + 1

    for attempt in range(start, 10000):  # max 9999 users per day
        user_id = f"{prefix}-{today}-{attempt:04d}"
        try:
            res = supabase.from_("users").select("user_id").eq("user_id", user_id).execute()
            # new client: check status_code instead of .error
            if hasattr(res, "status_code") and res.status_code >= 400:
                print("Supabase error fetching user_id:", getattr(res, "data", None))
                break
            if hasattr(res, "data") and not res.data:  # ID is free
                st.session_state.last_user_num[key] = attempt
                return user_id
        except Exception as e:
            print("Supabase exception:", e)
            break

    # fallback
    return f"{prefix}-{today}-0001"

def insert_user(data: dict):
    try:
        res = supabase.from_("users").insert(data).execute()
        if hasattr(res, "status_code") and res.status_code >= 400:
            return False, f"🚫 Supabase error: {getattr(res, 'data', res)}"
        return True, "✅ User registered successfully!"
    except Exception as e:
        return False, f"⚠️ Unexpected error: {e}"

def authenticate_user(username: str, password: str):
    try:
        res = supabase.from_("users").select("*").eq("username", username).execute()
        users = getattr(res, "data", [])
        if not users:
            return False, username, None
        user = users[0]
        if verify_password(password, user.get("password_hash", "")):
            if not user.get("is_active", True):
                return False, username, None
            return True, user.get("username"), user.get("role")
        return False, username, None
    except Exception as e:
        st.warning(f"⚠️ Unexpected authentication error: {e}")
        return False, username, None

def fetch_class_stream():
    default_classes = ["S.1","S.2","S.3","S.4","S.5","S.6"]
    default_streams = ["EAST","WEST","NORTH","SOUTH"]
    class_list, stream_list = [], []

    try:
        class_res = supabase.from_("class_options").select("name").execute()
        if hasattr(class_res, "status_code") and class_res.status_code >= 400:
            st.warning(f"⚠️ Could not fetch Class options: {getattr(class_res, 'data', class_res)}")
            class_list = default_classes
        else:
            class_list = [r["name"] for r in getattr(class_res, "data", [])] or default_classes
    except Exception as e:
        st.warning(f"⚠️ Could not fetch Class options: {e}")
        class_list = default_classes

    try:
        stream_res = supabase.from_("stream_options").select("name").execute()
        if hasattr(stream_res, "status_code") and stream_res.status_code >= 400:
            st.warning(f"⚠️ Could not fetch Stream options: {getattr(stream_res, 'data', stream_res)}")
            stream_list = default_streams
        else:
            stream_list = [r["name"] for r in getattr(stream_res, "data", [])] or default_streams
    except Exception as e:
        st.warning(f"⚠️ Could not fetch Stream options: {e}")
        stream_list = default_streams

    return class_list, stream_list


@st.dialog("📝 Register here", width="small")
def show_signup_dialog():
    import time

    st.markdown("""
        <style>
        .tight-label { color: #1E90FF; font-weight: 250; padding:0; margin:0; line-height:0.5; display:block; font-style:Times New Roman; }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div { margin-top:-5px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<span class="tight-label">Select Role</span>', unsafe_allow_html=True)
    role = st.selectbox("", ["Select role ..","Student","Parent","Teacher","Therapist","Admin","Admin2"])

    if role != "Select role ..":
        with st.form("signup_form"):
            # Initialize all fields
            first_name = last_name = full_name = username = email = password = confirm_password = None
            sex = age = class_ = stream = parent_guardian = profession = address = contact = None

            # --- Role-dependent fields ---
            # --- Student role form ---
            if role == "Student":
                st.markdown('<span class="tight-label">First Name</span>', unsafe_allow_html=True)
                first_name = st.text_input("", key="first_name")
                st.markdown('<span class="tight-label">Last Name</span>', unsafe_allow_html=True)
                last_name = st.text_input("", key="last_name")
                full_name = f"{first_name.strip()} {last_name.strip()}" if first_name and last_name else None

                st.markdown('<span class="tight-label">Sex</span>', unsafe_allow_html=True)
                sex = st.selectbox("", ["Male", "Female", "Other"])
                st.markdown('<span class="tight-label">Age</span>', unsafe_allow_html=True)
                age = st.number_input("", 3, 100, step=1)

                st.markdown('<span class="tight-label">Parent/Guardian</span>', unsafe_allow_html=True)
                parent_guardian = st.text_input("", key="parent_guardian")
                st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
                address = st.text_area("", key="address")
                st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
                contact = st.text_input("", key="contact")

                # --- Safely fetch Class & Stream dynamically ---
                class_list, stream_list = [], []

                try:
                    class_res = supabase.from_("class_options").select("name").execute()
                    if hasattr(class_res, "data") and class_res.data:
                        class_list = [r["name"] for r in class_res.data]
                except Exception as e:
                    pass
                    # st.info("⚠️ Class options unavailable; using defaults.")

                try:
                    stream_res = supabase.from_("stream_options").select("name").execute()
                    if hasattr(stream_res, "data") and stream_res.data:
                        stream_list = [r["name"] for r in stream_res.data]
                except Exception as e:
                    # st.info("⚠️ Stream options unavailable; using defaults.")
                    pass

                # --- Defaults if missing ---
                default_classes = ["S.1","S.2","S.3","S.4","S.5","S.6"]
                default_streams = ["EAST","WEST","NORTH","SOUTH"]

                class_list = default_classes + [c for c in class_list if c not in default_classes]
                stream_list = default_streams + [s for s in stream_list if s not in default_streams]

                st.markdown('<span class="tight-label">Class</span>', unsafe_allow_html=True)
                class_choice = st.selectbox("", class_list + ["Other"], key="class_select")
                class_ = st.text_input("Enter class", key="custom_class") if class_choice == "Other" else class_choice

                st.markdown('<span class="tight-label">Stream</span>', unsafe_allow_html=True)
                stream_choice = st.selectbox("", stream_list + ["Other"], key="stream_select")
                stream = st.text_input("Enter stream", key="custom_stream") if stream_choice == "Other" else stream_choice

            elif role in ["Parent","Teacher"]:
                st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
                full_name = st.text_input("", key="full_name")
                st.markdown('<span class="tight-label">Address</span>', unsafe_allow_html=True)
                address = st.text_area("", key="address")
                st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
                contact = st.text_input("", key="contact")

            elif role == "Therapist":
                st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
                full_name = st.text_input("", key="full_name")
                st.markdown('<span class="tight-label">Profession</span>', unsafe_allow_html=True)
                profession = st.text_input("", key="profession")
                st.markdown('<span class="tight-label">Phone</span>', unsafe_allow_html=True)
                contact = st.text_input("", key="contact")

            elif role in ["Admin","Admin2"]:
                st.markdown('<span class="tight-label">Full Name</span>', unsafe_allow_html=True)
                full_name = st.text_input("", key="full_name")

            # --- Common fields ---
            st.markdown('<span class="tight-label">Username</span>', unsafe_allow_html=True)
            username = st.text_input("", key="username")
            st.markdown('<span class="tight-label">Email</span>', unsafe_allow_html=True)
            email = st.text_input("", key="email")
            st.markdown('<span class="tight-label">Password</span>', unsafe_allow_html=True)
            password = st.text_input("", type="password", key="password")
            st.markdown('<span class="tight-label">Confirm Password</span>', unsafe_allow_html=True)
            confirm_password = st.text_input("", type="password", key="confirm_password")

            submitted = st.form_submit_button(":green[Create Account]")

            if submitted:
                if not username or not email or not password or not confirm_password or (role=="Student" and (not first_name or not last_name)):
                    st.warning("⚠️ Please fill all required fields")
                elif password != confirm_password:
                    st.warning("⚠️ Passwords do not match")
                else:
                    # --- Generate unique user_id ---
                    user_id = generate_user_id(role)
                    password_hash = hash_password(password)

                    data = {
                        "user_id": user_id,
                        "username": username,
                        "password_hash": password_hash,
                        "role": role,
                        "email": email or None,
                        "first_name": first_name or None,
                        "last_name": last_name or None,
                        "full_name": full_name or None,
                        "sex": sex or None,
                        "age": int(age) if age else None,
                        "class": class_ or None,
                        "stream": stream or None,
                        "address": address or None,
                        "parent_guardian": parent_guardian or None,
                        "contact": contact or None,
                        "profession": profession or None,
                        "is_active": 1
                    }

                    # --- Insert user with retry ---
                    max_retries = 3
                    for _ in range(max_retries):
                        success, msg = insert_user(data)
                        if success:
                            break
                        if "duplicate key" in msg.lower():
                            data["user_id"] = generate_user_id(role)
                        else:
                            break

                    if success:
                        # Save new Class/Stream if custom
                        try:
                            if class_ and class_ not in default_classes:
                                supabase.from_("class_options").insert({"name": class_}).execute()
                            if stream and stream not in default_streams:
                                supabase.from_("stream_options").insert({"name": stream}).execute()
                        except Exception as e:
                            st.warning(f"⚠️ Could not save custom class/stream: {e}")

                        st.success(msg)
                        time.sleep(2)
                        st.session_state.show_signup = False
                        st.session_state.show_login = True
                        st.rerun()
                    else:
                        st.error(msg)

        # Login link outside form
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(":orange[Already have an account?]")
        with col2:
            if st.button(":blue[👉 Go to Login]", key="to_login"):
                st.session_state.show_signup = False
                st.session_state.show_login = True
                st.rerun()
