import streamlit as st
import time
import random

st.markdown(
    """
    <style>
    .stAppDeployButton{  
        visibility: Hidden;
    }
    .stMainMenu{   
        visibility: Hidden;
    }
    .stChatMessage{
        background-color: #ffcccc
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width= 50)

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("SchedulO Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = ":material/supervisor_account:" if message["role"] == "user" else ":material/robot_2:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter Details.."):
    # Define avatars
    user_avatar = ":material/supervisor_account:"
    assistant_avatar = ":material/robot_2:"

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant", avatar=assistant_avatar):
        response = st.write_stream(response_generator())

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})