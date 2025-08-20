import streamlit as st
from supabase import create_client, Client

# ---------------- Supabase Client ----------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
SUPABASE_SERVICE_KEY = st.secrets["supabase"]["service_role_key"]

# Frontend-safe client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin client
def get_admin_client() -> Client:
    """Return a Supabase client with service role privileges."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Test function
def test_connection():
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        if response.data is not None:
            st.success("✅ Supabase connection successful!")
        else:
            st.warning("⚠️ Supabase connection OK but table empty or inaccessible.")
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
