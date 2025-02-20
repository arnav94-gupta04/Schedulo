import streamlit as st 

st.set_page_config(page_title="Signup", page_icon="🔓")

st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width= 100)
st.markdown("<h3 style='padding: 0px;' >Welcome to,</h3>", unsafe_allow_html= True)
st.markdown("<h1 style='padding: 0px;' >SchedulO.</h1>", unsafe_allow_html= True)

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

with st.form("Signup"):
    col1, col2 = st.columns(2)
    with col1:  
        user_fname = st.text_input("First Name")
    with col2:  
        user_lname = st.text_input("Last Name")
    
    em_add= st.text_input("Email Address")
    
    user_pass= st.text_input("Password")
    
    user_cp= st.text_input("Enter password again")
    
    required_fields = {
    "First Name": user_fname.strip(),
    "Last Name": user_lname.strip(),
    "Email Address": em_add.strip(),
    "Password": user_pass.strip(),
    "Confirmed Password": user_cp.strip(),
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    sub_state= st.form_submit_button("Submit")
    
    if sub_state:
        if missing_fields:
            st.warning(f"⚠️ Please fill in: {', '.join(missing_fields)}")
        else:
            st.balloons()
            st.info(f"Welcome, {user_fname} {user_lname}! Please login again to use SchedulO")
            st.form_submit_button("Login")
    