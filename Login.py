import streamlit as st

st.set_page_config(page_title="Login", page_icon="🔑")

st.markdown(
    """
    <style>
    .stAppDeployButton{  
        visibility: Hidden;
    }
    .stMainMenu{   
        visibility: Hidden;
    }
    .stForm{
        background-color: #ffcccc
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width= 100)
st.markdown("<h3 style='padding: 0px;' >Welcome to,</h3>", unsafe_allow_html= True)
st.markdown("<h1 style='padding: 0px;' >SchedulO.</h1>", unsafe_allow_html= True)

with st.form("Login"):
    user_id= st.text_input("Login_Id")
    user_pass= st.text_input("Password", type= "password")
    sub_state1, sub_state2= st.columns(2)
    sub_state1= st.form_submit_button("Login")
    sub_state2= st.form_submit_button("Sign Up")
    if sub_state1:
        if(user_id== "" or user_pass== ""):
            st.warning("Enter Correct Information or Sign up.")
        else:
            st.success("Succesfully Logged In")