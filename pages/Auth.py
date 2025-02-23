import streamlit as st
import sqlite3
from database import ScheduloDatabase

def create_users_table():
    conn = sqlite3.connect("schedulo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(first_name, last_name, email, password):
    conn = sqlite3.connect("schedulo.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect("schedulo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

create_users_table()

st.set_page_config(page_title="Schedulo - Login", page_icon="🔑")
#st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width=100)
st.markdown("<h1>Schedulo Authentication</h1>", unsafe_allow_html=True)

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# ---------------------
# LOGIN FORM
# ---------------------
if not st.session_state.show_signup:
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login")
    if login_submitted:
        if not email or not password:
            st.warning("Please fill in both email and password.")
        else:
            user = authenticate_user(email, password)
            if user:
                st.success(f"Welcome, {user[1]} {user[2]}!")
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.switch_page("Chatbot")
            else:
                st.error("Invalid email or password.")
    st.markdown("---")
    if st.button("Sign Up"):
        st.session_state.show_signup = True
        st.rerun()
else:
    # ---------------------
    # SIGNUP FORM
    # ---------------------
    st.header("Sign Up")
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
        with col2:
            last_name = st.text_input("Last Name")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submitted = st.form_submit_button("Create Account")
    if signup_submitted:
        if not first_name or not last_name or not email or not password or not confirm_password:
            st.warning("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success = add_user(first_name, last_name, email, password)
            if success:
                st.success("Signup successful! Please log in.")
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error("A user with this email already exists.")
    if st.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()
