DB_PATH = "users_db.db"
# # # from streamlit_option_menu import option_menu
# # # import streamlit as st
# # # from datetime import datetime
# # # import os
# # # import tempfile
# # # from moviepy.editor import VideoFileClip
# # # import json
# # # import hashlib
# # # from datetime import datetime, timedelta

# # # def get_video_details(video_bytes):
# # #     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
# # #         temp_file.write(video_bytes)
# # #         temp_file_path = temp_file.name
# # #     clip = VideoFileClip(temp_file_path)
# # #     duration = clip.duration 
# # #     resolution = f"{clip.size[0]}x{clip.size[1]}"  
# # #     clip.close()
# # #     return duration, resolution

# # # def save_video(video_bytes, video_name):
# # #     save_dir = "uploaded_videos"
# # #     if not os.path.exists(save_dir):
# # #         os.makedirs(save_dir)
# # #     video_path = os.path.join(save_dir, video_name)
# # #     with open(video_path, 'wb') as f:
# # #         f.write(video_bytes)
# # #     return video_path

# # # def save_metadata(video_name, video_size, duration, resolution, author, label, video_hash):
# # #     metadata = {
# # #         "name": video_name,
# # #         "size": video_size,
# # #         "duration": duration,
# # #         "resolution": resolution,
# # #         "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# # #         "views": 0,
# # #         "downloads": 0,
# # #         "likes": 0,
# # #         "author": author,
# # #         "label": label,
# # #         "hash": video_hash
# # #     }
# # #     metadata_path = "video_metadata.json"
# # #     if os.path.exists(metadata_path):
# # #         with open(metadata_path, 'r') as f:
# # #             all_metadata = json.load(f)
# # #     else:
# # #         all_metadata = []
# # #     all_metadata.append(metadata)
# # #     with open(metadata_path, 'w') as f:
# # #         json.dump(all_metadata, f, indent=4)
# # #     return metadata

# # # def save_video_metadata(metadata):
# # #     metadata_path = "video_metadata.json"
# # #     with open(metadata_path, 'w') as f:
# # #         json.dump(metadata, f, indent=4)

# # # def load_video_metadata():
# # #     metadata_path = "video_metadata.json"
# # #     if os.path.exists(metadata_path):
# # #         with open(metadata_path, 'r') as f:
# # #             return json.load(f)
# # #     return []

# # # def calculate_hash(video_bytes):
# # #     return hashlib.sha256(video_bytes).hexdigest()

# # # def video_exists(video_hash):
# # #     """Check if a video with the same hash already exists in the metadata."""
# # #     all_videos = load_video_metadata()
# # #     for video in all_videos:
# # #         if video['hash'] == video_hash:
# # #             return True
# # #     return False

# # # def update_metadata(video_name, action):
# # #     metadata_path = "video_metadata.json"
# # #     if os.path.exists(metadata_path):
# # #         with open(metadata_path, 'r') as f:
# # #             all_metadata = json.load(f)
# # #     else:
# # #         all_metadata = []
# # #     for video in all_metadata:
# # #         if video['name'] == video_name:
# # #             if action == "view":
# # #                 video['views'] = video.get('views', 0) + 1
# # #             elif action == "download":
# # #                 video['downloads'] = video.get('downloads', 0) + 1
# # #             elif action == "like":
# # #                 video['likes'] = video.get('likes', 0) + 1
# # #             break
# # #     with open(metadata_path, 'w') as f:
# # #         json.dump(all_metadata, f, indent=4)

# # # def get_latest_videos(metadata, hours=24):
# # #     recent_videos = []
# # #     now = datetime.now()
# # #     for video in metadata:
# # #         upload_time = datetime.strptime(video['upload_time'], '%Y-%m-%d %H:%M:%S')
# # #         if now - upload_time <= timedelta(hours=hours):
# # #             recent_videos.append(video)
# # #     recent_videos.sort(key=lambda x: datetime.strptime(x['upload_time'], '%Y-%m-%d %H:%M:%S'), reverse=True)
# # #     return recent_videos

# # # def main():
# # #     col1, col2 = st.columns(2)
# # #     author = col1.text_input('Author')
# # #     label = col2.text_input('Label')

# # #     if uploaded_video and author and label:
# # #         video_bytes = uploaded_video.read()
# # #         video_hash = calculate_hash(video_bytes)
# # #         if st.button('Upload Video'):
# # #             if video_exists(video_hash):
# # #                 st.error("This video has already been uploaded!")
# # #             else:
# # #                 video_name = uploaded_video.name
# # #                 video_size_mb = f"{len(video_bytes) / (1024 * 1024):.4f} MB"
# # #                 duration, resolution = get_video_details(video_bytes)
# # #                 save_video(video_bytes, video_name)
# # #                 save_metadata(video_name, video_size_mb, duration, resolution, author, label, video_hash)
# # #                 st.sidebar.success(f"Video '{video_name}' uploaded successfully!")

# # # if __name__ == '__main__':
# # #     main()


# # import streamlit as st
# # import sqlite3

# # from io import BytesIO

# # # DB setup: create table if not exists
# # def create_connection():
# #     conn = sqlite3.connect(DB_PATH)
# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS videos (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             name TEXT,
# #             data BLOB,
# #             upload_time TEXT
# #         )
# #     """)
# #     conn.commit()
# #     return conn

# # def save_video_to_db(conn, name, data, upload_time):
# #     cur = conn.cursor()
# #     cur.execute("INSERT INTO videos (name, data, upload_time) VALUES (?, ?, ?)", (name, data, upload_time))
# #     conn.commit()

# # def get_all_videos(conn):
# #     cur = conn.cursor()
# #     cur.execute("SELECT id, name, data FROM videos ORDER BY id DESC")
# #     return cur.fetchall()

# # def main():
# #     st.title("Video Upload and Playback with SQLite")

# #     conn = create_connection()

# #     uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])
# #     if uploaded_video is not None:
# #         video_bytes = uploaded_video.read()
# #         st.video(video_bytes)

# #         if st.button("Save Video to Database"):
# #             import datetime
# #             upload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             save_video_to_db(conn, uploaded_video.name, video_bytes, upload_time)
# #             st.success(f"Video '{uploaded_video.name}' saved successfully!")

# #     st.markdown("---")
# #     st.header("Saved Videos")

# #     videos = get_all_videos(conn)
# #     if not videos:
# #         st.info("No videos in database.")
# #     else:
# #         for vid in videos:
# #             st.write(f"**{vid[1]}**")
# #             st.video(vid[2])

# # if __name__ == "__main__":
# #     main()
# import streamlit as st
# import sqlite3

# import datetime

# # DB setup
# def create_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS videos (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             data BLOB,
#             upload_time TEXT
#         )
#     """)
#     conn.commit()
#     return conn

# def save_video_to_db(conn, name, data, upload_time):
#     cur = conn.cursor()
#     cur.execute("INSERT INTO videos (name, data, upload_time) VALUES (?, ?, ?)", (name, data, upload_time))
#     conn.commit()

# def get_all_videos(conn):
#     cur = conn.cursor()
#     cur.execute("SELECT id, name, data FROM videos ORDER BY id DESC")
#     return cur.fetchall()

# def main():
#     st.title("Record or Upload Video, Preview, and Save to DB")

#     conn = create_connection()

#     # Toggle switch to enable/disable webcam recorder
#     record_enabled = st.checkbox("Enable Webcam Recording")

#     if record_enabled:
#         st.subheader("1. Record Video Using Webcam")
#         recorded_video = st.camera_input("Record a video")

#         if recorded_video:
#             st.video(recorded_video)
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Discard Recorded Video"):
#                     st.info("Recorded video discarded.")
#                     st.experimental_rerun()
#             with col2:
#                 if st.button("Save Recorded Video"):
#                     video_bytes = recorded_video.getvalue()
#                     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     save_video_to_db(conn, f"recorded_{now}.mp4", video_bytes, now)
#                     st.success("Recorded video saved successfully!")
#                     st.experimental_rerun()

#     st.markdown("---")
#     st.subheader("2. Upload Video File")
#     uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])

#     if uploaded_video:
#         video_bytes = uploaded_video.read()
#         st.video(video_bytes)

#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Discard Uploaded Video"):
#                 st.info("Uploaded video discarded.")
#                 st.rerun()
#         with col2:
#             if st.button("Save Uploaded Video"):
#                 now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 save_video_to_db(conn, uploaded_video.name, video_bytes, now)
#                 st.success(f"Uploaded video '{uploaded_video.name}' saved successfully!")
#                 st.rerun()

#     st.markdown("---")
#     st.subheader("Saved Videos")

#     videos = get_all_videos(conn)
#     if not videos:
#         st.info("No videos in database.")
#     else:
#         for vid in videos:
#             st.write(f"**{vid[1]}**")
#             st.video(vid[2])

# if __name__ == "__main__":
#     main()
import streamlit as st
import sqlite3

import datetime

# DB Setup
def create_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            data BLOB,
            category TEXT,
            topic TEXT,
            label TEXT,
            uploaded_by TEXT,
            upload_time TEXT
        )
    """)
    conn.commit()
    return conn

def save_video_to_db(conn, name, data, category, topic, label, uploaded_by, upload_time):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO videos (name, data, category, topic, label, uploaded_by, upload_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, data, category, topic, label, uploaded_by, upload_time))
    conn.commit()

def get_all_videos(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM videos ORDER BY id DESC")
    return cur.fetchall()

def main():
    st.title("🎥 Upload & View Educational Videos")

    conn = create_connection()

    categories = ["Mental Disorders", "Self Help Techniques", "Therapy Tools", "Neuroscience", "Health Education"]
    st.subheader("📤 Upload a Video")

    category = st.selectbox("Select Category", categories)
    topic = st.text_input("Topic")
    label = st.text_input("Label (short title)")
    uploaded_by = st.text_input("Uploaded by")

    uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_video and category and topic and label and uploaded_by:
        video_bytes = uploaded_video.read()
        st.video(video_bytes)

        if st.button("Save Video"):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_video_to_db(conn, uploaded_video.name, video_bytes, category, topic, label, uploaded_by, now)
            st.success(f"Video '{label}' saved successfully!")

    st.markdown("---")
    st.subheader("📂 Filter & View Saved Videos")

    all_videos = get_all_videos(conn)
    if not all_videos:
        st.info("No videos saved yet.")
        return

    # Extract unique values for dynamic filters
    all_categories = sorted(set([v[3] for v in all_videos]))
    all_topics = sorted(set([v[4] for v in all_videos]))
    all_uploaders = sorted(set([v[6] for v in all_videos]))
    all_dates = [datetime.datetime.strptime(v[7], "%Y-%m-%d %H:%M:%S") for v in all_videos]

    selected_category = st.selectbox("Filter by Category", ["All"] + all_categories)
    selected_topic = st.selectbox("Filter by Topic", ["All"] + all_topics)
    label_search = st.text_input("Search by Label Keyword")
    selected_uploader = st.selectbox("Filter by Uploader", ["All"] + all_uploaders)

    # Date filter (Year, Month, Day)
    years = sorted(set([d.year for d in all_dates]))
    months = sorted(set([d.month for d in all_dates]))
    days = sorted(set([d.day for d in all_dates]))

    col1, col2, col3 = st.columns(3)
    selected_year = col1.selectbox("Year", ["All"] + [str(y) for y in years])
    selected_month = col2.selectbox("Month", ["All"] + [str(m).zfill(2) for m in months])
    selected_day = col3.selectbox("Day", ["All"] + [str(d).zfill(2) for d in days])

    # Apply filters
    filtered = []
    for v in all_videos:
        _, name, data, cat, top, lab, uploader, up_time = v
        dt = datetime.datetime.strptime(up_time, "%Y-%m-%d %H:%M:%S")

        if selected_category != "All" and cat != selected_category:
            continue
        if selected_topic != "All" and top != selected_topic:
            continue
        if selected_uploader != "All" and uploader != selected_uploader:
            continue
        if selected_year != "All" and str(dt.year) != selected_year:
            continue
        if selected_month != "All" and f"{dt.month:02d}" != selected_month:
            continue
        if selected_day != "All" and f"{dt.day:02d}" != selected_day:
            continue
        if label_search and label_search.lower() not in lab.lower():
            continue

        filtered.append(v)

    st.write(f"### 🎞️ {len(filtered)} video(s) found")
    for v in filtered:
        _, name, data, cat, top, lab, uploader, up_time = v
        st.markdown(f"**📝 Label:** {lab}  \n📚 **Topic:** {top}  \n🗂️ **Category:** {cat}  \n👤 **By:** {uploader}  \n🕒 **Uploaded on:** {up_time}")
        st.video(data)
        st.markdown("---")

if __name__ == "__main__":
    main()
