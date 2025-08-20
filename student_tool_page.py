import streamlit as st
import json
import pandas as pd
import os
import importlib
from datetime import datetime
import phq9_qn
import gad7_qn, caps_responses, snap_responses, ssq_responses, hsq_responses, ssq_qn, snap,hsq_qn
import bcrypt
import base64
from streamlit_card import card
import sqlite3

import bcrypt
from streamlit_option_menu import option_menu
from streamlit_javascript import st_javascript
import phq9_responses, gad7_responses, dass21_responses, dass21_qn, phq4_qn, phq4_responses, caps_form
import json
DB_PATH = "users_db.db"

## HELPER FXNS  #######
def styled_tasks_heading():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #6EE7B7, #3B82F6, #9333EA, #F59E0B);
        width: 100%;
        padding: 1.2rem 0.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        margin-bottom: 1rem;
        animation: fadeIn 5s ease-in-out;
    ">
        <h3 style="
            font-size: 2.3rem;
            font-family: 'Trebuchet MS', sans-serif;
            color: #ffffff;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            margin: 0;
        ">📝 TASKS</h3>
        <p style="
            font-size: 1.1rem;
            color: #f0f8ff;
            margin-top: 0.4rem;
            font-style: italic;
        ">Stay on track. Complete your screenings, view progress, and take action!</p>
    </div>

    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)



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



def create_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None


def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()[0]
        return result > 0
    except Exception as e:
        st.error(f"An error occurred while checking for duplicates: {e}")
        return False
    finally:
        cursor.close()

def fetch_student_by_username(db, username):
    cursor = db.cursor()
    select_student_query = """
    SELECT user_id, full_name, age, class, stream, username, email, contact, password_hash
    FROM users
    WHERE username = ?
    """
    cursor.execute(select_student_query, (username,))
    student = cursor.fetchone()
    cursor.close()
    return student

###### EDIT RECORDS ###########

from datetime import datetime

def edit_student_record(db, user_id, appointment_id, new_age, new_class, new_stream):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE users
            SET age = ?, class = ?, stream = ?, last_updated = ?
            WHERE user_id = ?
        """, (new_age, new_class, new_stream, now, user_id))

        cursor.execute("""
            UPDATE appointments
            SET age = ?, class = ?, stream = ?, last_profile_update = ?
            WHERE appointment_id = ?
        """, (new_age, new_class, new_stream, now, appointment_id))

        db.commit()
        st.session_state.update_success = now

    except Exception as e:
        st.error(f"❌ Failed to update student and appointment record: {e}")
    finally:
        cursor.close()


def edit_student(db):
    if 'edit_student' in st.session_state and st.session_state.edit_student:
        student = st.session_state.edit_student
        with st.form('Edit form'):
            new_age = st.number_input("AGE (yrs)", value=student['age'], min_value=1, step=1)
            class_index = class_list.index(student['student_class']) if student['student_class'] in class_list else 0
            new_class = st.selectbox("CLASS", class_list, index=class_index)
            stream_index = stream_list.index(student['stream']) if student['stream'] in stream_list else 0
            new_stream = st.selectbox("STREAM", stream_list, index=stream_index)
            update = st.form_submit_button('Update')
            if update:
                edit_student_record(
                    db,
                    student['user_id'],
                    st.session_state.get("appointment_id"),
                    new_age,
                    new_class,
                    new_stream,)
                st.session_state.edit_student.update({
                    'age': new_age,
                    'student_class': new_class,
                    'stream': new_stream,
                })
                st.rerun()
        if st.session_state.get('update_success'):
            st.success(f"✅ Record updated at {st.session_state['update_success']}")
            del st.session_state['update_success']


def search_edit_and_update_student(db, username):
    if username:
        student = fetch_student_by_username(db, username)
        if student:
            student_dict = {
                'user_id': student[0],
                'name': student[1],
                'age': student[2],
                'student_class': student[4],
                'stream': student[5],
                'username': student[6],
                'email': student[7],
                'contact': student[8]
            }
            st.session_state.edit_student = student_dict
            edit_student(db)
            return True  # <-- Add this
        else:
            st.error("Student record not found in the database.")
            return False  # <-- Add this
    return False


def check_functioning_completed(db, appointment_id):
    cursor = db.cursor()
    query = "SELECT difficulty_level FROM functioning_responses WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchone()
    cursor.close()
    return result


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def table_exists(db, table_name):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


#### FXNING RESPONSES ########

def create_functioning_responses_table(db):
    cursor = db.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS functioning_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            difficulty_level TEXT NOT NULL CHECK(difficulty_level IN ('Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult')),
            fnx_score INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        cursor.execute(create_table_query)
        db.commit()
        print("Table 'functioning_responses' ensured.")
    except Exception as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()



def insert_functioning_response(db, appointment_id, user_id, difficulty_level):
    cursor = db.cursor()
    difficulty_to_score = {
        "Extremely difficult": 1,
        "Very difficult": 2,
        "Somewhat difficult": 3,
        "Not difficult at all": 4
    }
    fnx_score = difficulty_to_score.get(difficulty_level)
    if fnx_score is None:
        st.error("Invalid difficulty level.")
        return False

    insert_query = """
    INSERT INTO functioning_responses (appointment_id, user_id, difficulty_level, fnx_score)
    VALUES (?, ?, ?, ?)
    """
    try:
        cursor.execute(insert_query, (appointment_id, user_id, difficulty_level, fnx_score))
        db.commit()
        return True
    except Exception as err:
        st.error(f"Error inserting response: {err}")
        return False
    finally:
        cursor.close()



def get_phq4_score(db, appointment_id):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT total_score FROM PHQ4_forms WHERE appointment_id = ?", (appointment_id,))
        result = cursor.fetchone()
        if result:
            return result[0] 
        return None
    except Exception as e:
        st.error(f"Error fetching PHQ-4 score: {e}")
        return None
    finally:
        cursor.close()
if "phq4_popup_shown" not in st.session_state:
    st.session_state.phq4_popup_shown = {}

# @st.dialog("🧠 Additional Assessment Required")
@st.dialog("🧠 Additional Assessment Required")
def phq4_popup(username, appointment_id):
    username = st.session_state.get("user_name")
    st.markdown(
        f"""
        Dear **{username}**, based on your scores on PHQ-4, you're kindly required to fill additional forms 
        to help us understand your mental health status better.

        Please be honest and complete the next assessments carefully. Your wellbeing matters. 💙

        Thank you.
        """
    )
    if st.button("✅ Proceed", key=f"proceed_button_{appointment_id}"):
        st.session_state.phq4_popup_shown[appointment_id] = True
        st.rerun()

#### FECT DETAILS OF STUDENTS ##########3

def add_last_updated_column():
    db = create_connection()
    try:
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cursor.fetchall()]
        if "last_updated" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_updated TEXT;")
            db.commit()
            now = datetime.now().isoformat()
            cursor.execute("UPDATE users SET last_updated = ?", (now,))
            db.commit()
            st.success("✅ 'last_updated' column added and initialized.")
        else:
            st.info("ℹ️ 'last_updated' column already exists.")
    except Exception as e:
        st.error(f"Error adding 'last_updated' column: {e}")
    finally:
        cursor.close()
        db.close()



# #### UTILS ####
class_list = ['','S1', 'S2', 'S3', 'S4', 'S5', 'S6']
stream_list = ['',"EAST", "SOUTH", 'WEST', 'NORTH']
gender_list = ['','MALE','FEMALE']

tool_modules = {
    'PHQ-9': phq9_qn.main,
    'GAD-7':gad7_qn.main,
    'DASS-21': dass21_qn.main,
    'PHQ-4': phq4_qn.main,

    'CAPS-14':caps_form.main,
    'SSQ':ssq_qn.main,
    'HSQ':hsq_qn.main,
    'SNAP-IV-C': snap.main,
}
response_modules = {
    'PHQ-9': phq9_responses.main,
    'GAD-7':gad7_responses.main,
    'Functioning': 'Noted',
    'DASS-21': dass21_responses.main, 
    'PHQ-4':phq4_responses.main,

     'CAPS-14':caps_responses.main,
    'SSQ':ssq_responses.main,
    'HSQ':hsq_responses.main,
    'SNAP-IV-C':snap_responses.main,}


def is_tool_completed(db, tool, appointment_id):
    table_map = {
        "PHQ-4": "PHQ4_forms",
        "PHQ-9": "PHQ9_forms",
        "GAD-7": "GAD7_forms",
        "DASS-21": "DASS21_forms",
        "BDI": "BDI_forms",
        "SRQ": "SRQ_forms",
        "CAPS-14": "CAPS_forms",
        "HSQ": "HSQ_forms",
        "SSQ": "SSQ_forms",
        "SNAP-IV-C": "SNAPIVC_forms"
    }
    table_name = table_map.get(tool)
    if not table_name:
        return False
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT responses_dict FROM {table_name} WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        return bool(row and row["responses_dict"])
    except Exception:
        return False

def parse_screening_tools(screening_json):
    try:
        tools = json.loads(screening_json)
        return {tool: data.get("status", "Pending") for tool, data in tools.items()}
    except Exception:
        return {}


def display_functioning_questionnaire(db, appointment_id, student_id):
    completed_response = check_functioning_completed(db, appointment_id)
    if completed_response:
        st.success(f"Functioning completed ✅")
    else:
        st.info("If you checked off any problems, how difficult have these problems made it for you?")
        difficulty_level = st.radio(
            "Choose difficulty level:",
            ('Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult'))

        if st.button("Submit Functioning Response"):
            success = insert_functioning_response(db, appointment_id, student_id, difficulty_level)
            if success:
                st.success("Functioning response recorded successfully ✅!")
                st.rerun() 

def fetch_requested_tools(db, appointment_id):
    table_name = "appointments"
    if not table_exists(db, table_name):
        st.warning(f"Table '{table_name}' does not exist.")
        return {}
    try:
        cursor = db.cursor()
        fetch_query = """
            SELECT screening_tools
            FROM appointments
            WHERE appointment_id = ?
            AND actions LIKE '%"screen": true%'
            ORDER BY appointment_id DESC
            LIMIT 1
        """
        cursor.execute(fetch_query, (appointment_id,))
        result = cursor.fetchone()
        if not result:
            return {}

        screening_tools_json = result["screening_tools"]
        tools_dict = json.loads(screening_tools_json) if screening_tools_json else {}
        tools_status = {tool: info.get("status", "Pending") for tool, info in tools_dict.items()}
        return tools_status

    except Exception as e:
        st.error(f"Database error fetching requested tools: {e}")
        return {}
    finally:
        cursor.close()

def parse_screening_tools(screening_json):
    try:
        tools = json.loads(screening_json)
        return {tool: data.get("status", "Pending") for tool, data in tools.items()}
    except Exception:
        return {}
def update_tool_status(db, appointment_id, tool_name, new_status):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT screening_tools FROM appointments WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        tools_dict = json.loads(row["screening_tools"] or '{}') if row else {}

        if tool_name in tools_dict:
            tools_dict[tool_name]["status"] = new_status
            tools_dict[tool_name]["response_date"] = datetime.today().strftime("%Y-%m-%d")
        else:
            tools_dict[tool_name] = {
                "status": new_status,
                "response_date": datetime.today().strftime("%Y-%m-%d"),
                "scheduled_date": datetime.today().strftime("%Y-%m-%d")
            }

        cursor.execute("UPDATE appointments SET screening_tools = ? WHERE appointment_id = ?",
                       (json.dumps(tools_dict), appointment_id))
        db.commit()
        return True
    except Exception as e:
        st.error(f"Failed to update tool status: {e}")
        return False
    finally:
        cursor.close()

def get_requested_tools(db, appointment_id):
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT screening_tools FROM appointments
            WHERE appointment_id = ? AND actions LIKE '%"screen": true%'
            ORDER BY appointment_id DESC
            LIMIT 1
        """, (appointment_id,))
        row = cursor.fetchone()
        if row:
            tools_json = row["screening_tools"]
            if tools_json:
                tools_dict = json.loads(tools_json)
                return {tool: info.get("status", "Pending") for tool, info in tools_dict.items()}
        return {}
    except Exception as e:
        st.error(f"Error fetching requested tools: {e}")
        return {}
    finally:
        cursor.close()

def parse_screening_tools(screening_json):
    try:
        tools = json.loads(screening_json)
        return {tool: data.get("status", "Pending") for tool, data in tools.items()}
    except Exception:
        return {}

def fetch_appointments_details_by_username(username):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT 
                    s.appointment_id, s.user_id, s.name, s.appointment_type, s.screen_type, s.term,
                    s.appointment_date, s.appointment_time,
                    s.class, s.stream, s.client_type, s.actions,
                    s.assigned_therapist, s.screening_tools
                FROM appointments s
                JOIN users u ON s.user_id = u.user_id
                WHERE u.username = ? AND s.actions LIKE '%"screen": true%'
                ORDER BY s.created_at DESC
            """

            cursor.execute(query, (username,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            records = []
            for row in rows:
                record = dict(zip(columns, row))
                try:
                    record["tools_statuses"] = parse_screening_tools(record["screening_tools"])
                except Exception as e:
                    st.warning(f"Failed to parse screening_tools for appointment_id {record['appointment_id']}: {e}")
                    record["tools_statuses"] = {}
                records.append(record)
            return records
        except Exception as e:
            st.error(f"Error fetching screening data: {e}")
        finally:
            cursor.close()
            connection.close()
    return []
def add_last_profile_update_column(db):
    try:
        cursor = db.cursor()

        # Check if the column already exists
        cursor.execute("PRAGMA table_info(appointments)")
        columns = [row[1] for row in cursor.fetchall()]

        if "last_profile_update" not in columns:
            cursor.execute("ALTER TABLE appointments ADD COLUMN last_profile_update TEXT")
            db.commit()
            st.success("✅ 'last_profile_update' column added to appointments table.")
        else:
            st.info("ℹ️ 'last_profile_update' column already exists.")
    except Exception as e:
        st.error(f"❌ Failed to add column: {e}")
    finally:
        cursor.close()

def update_screen_action_status(db, appointment_id):
    try:
        cursor = db.cursor()

        cursor.execute("SELECT screening_tools, statuses FROM appointments WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        if not row:
            return

        screening_tools = json.loads(row["screening_tools"] or '{}')
        statuses = json.loads(row["statuses"] or '{}')

        if screening_tools:
            any_incomplete = any(
                tool_data.get("status") not in ("Completed", "NA")
                for tool_data in screening_tools.values()
            )
            status_value = "Pending" if any_incomplete else "Completed"
            statuses["screen"] = {
                "status": status_value,
                "completion_date": datetime.today().strftime("%Y-%m-%d") if status_value == "Completed" else None
            }
        else:
            statuses["screen"] = {
                "status": "Pending",
                "completion_date": None
            }

        cursor.execute(
            "UPDATE appointments SET statuses = ? WHERE appointment_id = ?",
            (json.dumps(statuses), appointment_id)
        )
        db.commit()
    except Exception as e:
        st.error(f"Error updating screen status dynamically: {e}")
    finally:
        cursor.close()


def create_concerns_table(db):
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concerns (
            appointment_id TEXT PRIMARY KEY,
            user_id TEXT,
            concerns_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    cursor.close()

def save_concerns(db, appointment_id, user_id, concerns_text):
    cursor = db.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO concerns (appointment_id, user_id, concerns_text)
        VALUES (?, ?, ?)
    """, (appointment_id, user_id, concerns_text))
    db.commit()
    cursor.close()

def get_concerns(db, appointment_id):
    cursor = db.cursor()
    cursor.execute("SELECT concerns_text FROM concerns WHERE appointment_id = ?", (appointment_id,))
    row = cursor.fetchone()
    cursor.close()
    return row["concerns_text"] if row else None

def all_tools_completed(requested_tools):
    return all(status.strip() in ("Completed", "NA") for status in requested_tools.values())


@st.dialog("💬 Any current concerns")
def concerns_dialog(db, appointment_id, user_id):
    st.markdown("""
        <h4 style='color:skyblue;font-size:25px;'>We're here to listen.</h4>
        <p style='font-size:20px;'>Your thoughts help build a better mental health experience for everyone.</p>
    """, unsafe_allow_html=True)

    feedback = st.text_area("Your message:", height=200, placeholder="I feel...")
    if st.button("✅ Submit"):
        if feedback.strip():
            save_concerns(db, appointment_id, user_id, feedback.strip())
            st.success("Thank you for sharing 💚")
            st.rerun()
        else:
            st.warning("Please enter your thoughts before submitting.")
def search_edit_and_update_student(db, username):
    """
    Fetches the student by username, sets up session state for editing,
    and displays profile info safely without AttributeError.
    """
    if not username:
        st.warning("Username not provided.")
        return False

    student = fetch_student_by_username(db, username)
    if not student:
        st.error("⚠️ Student record not found in the database.")
        return False

    # Convert sqlite3.Row to a dictionary
    student_dict = {
        'user_id': student['user_id'],
        'name': student['name'],
        'age': student['age'],
        'student_class': student['class'],
        'stream': student['stream'],
        'username': student['username'],
        'email': student['email'],
        'contact': student['contact'],
        'gender': student['gender'] if 'gender' in student.keys() else ''
    }

    # Store in session state
    st.session_state.edit_student = student_dict

    # Display profile safely
    st.markdown(f"**User ID:** {student_dict['user_id']}")
    st.markdown(f"**Name:** {student_dict['name']}")
    st.markdown(f"**Gender:** {student_dict.get('gender', '')}")
    st.markdown(f"**Age:** {student_dict['age']} Years")
    st.markdown(f"**Class:** {student_dict['student_class']}")
    st.markdown(f"**Stream:** {student_dict['stream']}")
    st.markdown(f"**Contact:** {student_dict.get('contact', '')}")
    st.markdown(f"**Username:** {student_dict['username']}")
    st.markdown(f"**Email:** {student_dict.get('email', '')}")

    # Launch the edit form
    edit_student(db)

    return True


def fetch_student_by_username(db, username):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    student = cursor.fetchone()  # Returns None if not found
    cursor.close()
    return student

def create_connection():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # <-- allows row["column_name"]
    return conn

def search_edit_and_update_student(db, username):
    if not username:
        st.warning("Username not provided.")
        return False
    student = fetch_student_by_username(db, usernam)
    if not student:
        st.error("⚠️ Student record not found in the database.")
        return False

    # Store in session state for editing
    st.session_state.edit_student = {
        'user_id': student.get('user_id', ''),
        'name': student.get('name', ''),
        'age': student.get('age', ''),
        'student_class': student.get('class', ''),
        'stream': student.get('stream', ''),
        'username': student.get('username', ''),
        'email': student.get('email', ''),
        'contact': student.get('contact', ''),
        'gender': student.get('gender', '')
    }

    # Display profile safely
    st.markdown(f"**User ID:** {student.get('user_id', '')}")
    st.markdown(f"**Name:** {student.get('name', '')}")
    st.markdown(f"**Gender:** {student.get('gender', '')}")
    st.markdown(f"**Age:** {student.get('age', '')} Years")
    st.markdown(f"**Class:** {student.get('class', '')}")
    st.markdown(f"**Stream:** {student.get('stream', '')}")
    st.markdown(f"**Contact:** {student.get('contact', '')}")
    st.markdown(f"**Username:** {student.get('username', '')}")
    st.markdown(f"**Email:** {student.get('email', '')}")

    # Launch the edit form
    edit_student(db)

    return True


def main():
    db = create_connection()
    create_concerns_table(db)
    create_functioning_responses_table(db)
    set_full_page_background('images/black_strip.jpg')

    required_session_keys = ['user_name', "name", "selected_appointment", "appointment_id", "user_id"]
    for key in required_session_keys:
        if key not in st.session_state:
            st.session_state[key] = None

    username = st.session_state.get("user_name")
    device_width = st_javascript("window.innerWidth", key="device_width")
    if device_width is None:
        st.stop()
    is_mobile = device_width < 705

    # Layout settings
    num_cols_app = 3 if not is_mobile else 1
    appointment_card_height = "150px" if is_mobile else "200px"
    appointment_card_width = "100%"
    appointment_font_size_title = "18px" if is_mobile else "22px"
    appointment_font_size_text = "16px" if is_mobile else "18px"

    num_cols_tool = 4 if not is_mobile else 2
    tool_card_width = "100%"
    tool_card_height = "100px" if is_mobile else "150px"
    tool_font_size_title = "20px" if is_mobile else "25px"
    tool_font_size_text = "16px" if is_mobile else "18px"

    appointment_details = sorted(
        fetch_appointments_details_by_username(username),
        key=lambda x: (x["appointment_date"], x["appointment_time"]),
        reverse=True
    )

    # Back button
    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.session_state.get("selected_tool"):
            if st.button("🔙 Back", key="back_to_tool_menu"):
                st.session_state.selected_tool = None
                st.rerun()
        elif st.session_state.get("selected_appointment"):
            if st.button("🔙 Back", key="back_to_appointments"):
                st.session_state.selected_appointment = None
                st.session_state.appointment_id = None
                st.rerun()

    # === APPOINTMENTS LIST ===
    if st.session_state.get("selected_appointment") is None:
        if appointment_details:
            cols = st.columns(num_cols_app, gap="small")
            for index, appointment in enumerate(appointment_details):
                with cols[index % num_cols_app]:
                    appointment_id = appointment["appointment_id"]
                    user_id = appointment["user_id"]
                    name = appointment["name"]
                    screen_type = appointment["screen_type"]

                    appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
                    tool_statuses = list(appointment.get("tools_statuses", {}).values())
                    status_text = "Completed ✅" if all(status.strip() in ("Completed", "NA") for status in tool_statuses) else "Pending ⏳"
                    title = ordinal(len(appointment_details) - index)

                    hasClicked = card(
                        title=f'{title} - {screen_type}',
                        text=f"{appointment_id}\n{status_text}",
                        url=None,
                        styles={
                            "card": {
                                "width": appointment_card_width,
                                "height": appointment_card_height,
                                "margin": "0px",
                                "border-radius": "3px",
                                "background": appointment_color,
                                "color": "white",
                                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                "border": "0.1px solid #600000",
                                "text-align": "center",
                            },
                            "text": {"font-family": "serif", "font-size": appointment_font_size_text},
                            "title": {"font-family": "serif", "font-size": appointment_font_size_title}
                        },
                    )
                    if hasClicked:
                        st.session_state.selected_appointment = appointment
                        st.session_state.appointment_id = appointment_id
                        st.session_state.user_id = user_id
                        st.session_state.name = name
                        st.rerun()
        else:
            st.warning("No appointments found.")
        db.close()
        return

    # === PROFILE UPDATE ENFORCEMENT ===

    selected_appointment = st.session_state.get("selected_appointment")
    appointment_id = selected_appointment.get("appointment_id") if selected_appointment else None
    user_id = selected_appointment.get("user_id") if selected_appointment else None
    username = st.session_state.get("user_name")

    # Safety check: make sure we have a user_id
    if not user_id:
        st.warning("⚠️ User ID for this appointment was not found. Cannot update profile.")
        db.close()
        st.stop()

    # Enforce profile update before proceeding
    profile_key = f"profile_confirmed_{appointment_id}"
    if not st.session_state.get(profile_key):
        st.info("Please update your profile before proceeding.")
        student_found = search_edit_and_update_student(db, 'jane')

        if not student_found:
            st.warning("⚠️ Student record not found in the database. Please check your data.")
            db.close()
            st.stop()

        if st.button("✅ Confirm Profile Updated"):
            st.session_state[profile_key] = True
            st.rerun()

    # === TOOL SELECTION ===
    if st.session_state.get("selected_tool") is None:
        requested_tools = fetch_requested_tools(db, appointment_id)
        tools_list = list(requested_tools)
        if not tools_list:
            st.warning("No requested tools found.")
            db.close()
            return

        visible_tools = ["PHQ-4"]
        phq4_score = get_phq4_score(db, appointment_id)

        if phq4_score is not None and phq4_score >= 3:
            if "PHQ-9" in tools_list:
                visible_tools.append("PHQ-9")
            if "GAD-7" in tools_list:
                visible_tools.append("GAD-7")

        other_independent_tools = [tool for tool in tools_list if tool not in ("PHQ-4", "PHQ-9", "GAD-7", "PROFILE")]
        visible_tools.extend(other_independent_tools)

        if other_independent_tools:
            visible_tools.append("Functioning")

        all_completed = all_tools_completed(requested_tools)
        existing_concerns = get_concerns(db, appointment_id)
        if all_completed:
            visible_tools = ["Concerns"] + [t for t in visible_tools if t != "Concerns"]

        # Render tool cards
        tool_colors = {tool: f"#{hex(hash(tool) % 0xFFFFFF)[2:].zfill(6)}" for tool in visible_tools}
        tool_cols = st.columns(num_cols_tool, gap="small")
        for index, tool in enumerate(visible_tools):
            if tool == "Functioning":
                tool_status = check_functioning_completed(db, appointment_id)
                tool_status = "Completed" if tool_status and tool_status[0] else "Pending"
            elif tool == "Concerns":
                tool_status = "Completed" if existing_concerns else "Pending"
            else:
                tool_status = requested_tools.get(tool, "Pending")

            display_text = "Completed ✅" if tool_status == "Completed" else "Pending ⏳"
            if tool == "Concerns":
                display_text = f"Shared: {existing_concerns[:77] + '...' if existing_concerns and len(existing_concerns) > 80 else existing_concerns}" if existing_concerns else "Not shared"

            with tool_cols[index % num_cols_tool]:
                clicked = card(
                    title=tool,
                    text=display_text,
                    url=None,
                    styles={
                        "card": {
                            "width": tool_card_width,
                            "height": tool_card_height,
                            "margin": "0px",
                            "border-radius": "2px",
                            "background": tool_colors[tool],
                            "color": "white",
                            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                            "border": "0.1px solid #600000",
                            "text-align": "center",
                        },
                        "text": {"font-family": "serif", "font-size": tool_font_size_text},
                        "title": {"font-family": "serif", "font-size": tool_font_size_title}
                    },
                )
                if clicked:
                    st.session_state.selected_tool = tool
                    st.rerun()

    # === TOOL HANDLER ===
    else:
        selected_tool = st.session_state.selected_tool
        requested_tools = get_requested_tools(db, appointment_id)
        tool_status = requested_tools.get(selected_tool, "Pending")
        phq4_score = get_phq4_score(db, appointment_id)

        if selected_tool in ("PHQ-9", "GAD-7"):
            if phq4_score is None:
                st.info("Please complete PHQ-4 screening first.")
            elif phq4_score < 3:
                update_tool_status(db, appointment_id, selected_tool, "NA")
                update_screen_action_status(db, appointment_id)
                st.info(f"{selected_tool} marked as NA due to PHQ-4 score < 3")
            st.session_state.selected_tool = None
            st.rerun()
        else:
            if tool_status != "Completed":
                tool_modules[selected_tool]()
                with st.form(f"{selected_tool}_form"):
                    submitted = st.form_submit_button(f"✅ Submit to complete {selected_tool}")
                    if submitted:
                        if update_tool_status(db, appointment_id, selected_tool, "Completed"):
                            update_screen_action_status(db, appointment_id)
                            st.toast(f"{selected_tool} marked as Completed ✅", icon="✅")
                            st.session_state.selected_tool = None
                            st.rerun()
                    else:
                        response_modules[selected_tool]()

    db.close()

if __name__ == "__main__":
    main()
