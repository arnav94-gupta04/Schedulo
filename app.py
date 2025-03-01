import streamlit as st

st.set_page_config(page_title="Schedulo", page_icon="📅", layout="wide")

st.markdown(
    """
    <style>
    /* Hides the sidebar navigation */
    [data-testid="stSidebarNav"] { 
        display: none; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    st.switch_page("pages/Chatbot.py")
else:
    st.switch_page("pages/Auth.py")
