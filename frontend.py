import streamlit as st
from streamlit_oauth import OAuth2Component
from main import run_sync_for_user

# Load credentials from Streamlit Secrets
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.events']

st.set_page_config(page_title="AutoScheduler", page_icon="🎓", layout="centered")

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, "")

if "auth" not in st.session_state:
    st.title("🎓 AutoScheduler")
    st.info("Log in to automatically scan your Gmail for deadlines and workshops.")
    
    result = oauth2.authorize_button(
        name="Continue with Google",
        icon="https://www.google.com.tw/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope=" ".join(SCOPES),
        key="google_auth",
    )
    
    if result:
        st.session_state["auth"] = result
        st.rerun()
else:
    st.title("🚀 Sync Dashboard")
    st.write("Welcome! Click below to start the scan.")

    if st.button("🔄 Sync My Schedule Now", use_container_width=True):
        with st.status("Analyzing your emails...", expanded=True) as status:
            token = st.session_state["auth"]["token"]
            results = run_sync_for_user(token)
            
            if results:
                status.update(label=f"Done! Found {len(results)} events.", state="complete")
                st.balloons()
                st.subheader("✅ Newly Added Events")
                st.table(results)
            else:
                status.update(label="No New Events Found", state="complete")
                st.info("Everything is up to date!")

    if st.sidebar.button("Log Out"):
        del st.session_state["auth"]
        st.rerun()