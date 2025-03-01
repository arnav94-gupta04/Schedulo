import streamlit as st
import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from Version02.database import ScheduloDatabase

st.set_page_config(page_title="Schedulo - Chatbot", page_icon="🤖")

load_dotenv()
client = Groq()


# -----------------------------------
# Extraction using Groq API
# -----------------------------------
def build_extraction_prompt(input_text):
    prompt = f"""
You are an extractor. Given the following unstructured text about a university timetable, extract and output a JSON object with exactly the following keys:

- "academic_years": an array of strings representing academic years (e.g., ["FE", "SE", "TE", "BE"]).
- "divisions": an array of objects, each with keys "year" and "division" (e.g., {{"year": "SE", "division": "SE1"}}).
- "batches": an array of objects, each with keys "division" and "batch" (e.g., {{"division": "SE1", "batch": "S1"}}).
- "subjects": an array of objects, each with keys "code", "name", "year", "type", and "min_hours_per_week" (e.g., {{"code": "CS101", "name": "DBMS", "year": "SE", "type": "Lecture", "min_hours_per_week": 3}}).
- "teachers": an array of objects, each with keys "code", "name", "max_workload", and "subjects" (an array of subject codes; if none, output an empty array).
- "venues": an array of objects, each with keys "name" and "type" (e.g., {{"name": "Room 101", "type": "Classroom"}}).

For any missing value, output null (or an empty array for fields that expect arrays).  
Output only valid, complete JSON without any markdown formatting or backticks. Do not include any extra commentary or reasoning.

Input text:
{input_text}

Output:
"""
    return prompt.strip()

def extract_information(input_text):
    extraction_prompt = build_extraction_prompt(input_text)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": extraction_prompt}],
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None
    )
    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content
            time.sleep(0.02)
    
    # Clean up the response text
    response_text = response_text.strip()
    # Remove backticks and any markdown formatting
    response_text = response_text.replace('`', '').strip()
    
    try:
        info = json.loads(response_text)
        return info
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}\nResponse was:\n{repr(response_text)}")
        # Try to clean up common JSON formatting issues
        try:
            # Remove any potential BOM or invisible characters
            response_text = response_text.encode().decode('utf-8-sig')
            # Replace any Windows-style line endings
            response_text = response_text.replace('\r\n', '\n')
            info = json.loads(response_text)
            return info
        except Exception as e:
            st.error(f"Failed to parse JSON even after cleanup: {str(e)}")
            return None
        
# -----------------------------------
# Streamlit Chatbot UI
# -----------------------------------
st.markdown(
    """
    <style>
    .stAppDeployButton{ visibility: hidden; }
    .stMainMenu{ visibility: hidden; }
    .stChatMessage{ background-color: #ffcccc; }
    </style>
    """,
    unsafe_allow_html=True
)
#st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width=50)
st.title("Schedulo Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    avatar = ":material/supervisor_account:" if message["role"] == "user" else ":material/robot_2:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Initialize database (from your separate database.py)
db = ScheduloDatabase()

# Accept user input
if user_input := st.chat_input("Enter scheduling details:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=":material/supervisor_account:"):
        st.markdown(user_input)
    
    # Extract structured information using Groq API
    info = extract_information(user_input)
    
    if info is not None:
        # Store academic years
        academic_years = info.get("academic_years", [])
        for year in academic_years:
            db.insert_academic_year(year)
        
        # Store divisions
        divisions = info.get("divisions", [])
        for d in divisions:
            db.insert_division(d.get("year"), d.get("division"))
        
        # Store batches
        batches = info.get("batches", [])
        for b in batches:
            db.insert_batch(b.get("division"), b.get("batch"))
        
        # Store subjects
        subjects = info.get("subjects", [])
        for s in subjects:
            try:
                hours = int(s.get("min_hours_per_week"))
            except:
                hours = 0
            db.insert_subject(s.get("code"), s.get("name"), s.get("year"), s.get("type"), hours)
        
        # Store teachers and assign subjects
        teachers = info.get("teachers", [])
        for t in teachers:
            try:
                workload = int(t.get("max_workload"))
            except:
                workload = 0
            db.insert_teacher(t.get("code"), t.get("name"), workload)
            for subj in t.get("subjects", []):
                db.insert_teacher_subject(t.get("code"), subj)
        
        # Store venues
        venues = info.get("venues", [])
        for v in venues:
            db.insert_venue(v.get("name"), v.get("type"))
        
        ack = (
            "Stored information successfully:\n"
            f"Academic Years: {len(academic_years)}, Divisions: {len(divisions)}, Batches: {len(batches)}, "
            f"Subjects: {len(subjects)}, Teachers: {len(teachers)}, Venues: {len(venues)}."
        )
    else:
        ack = "No valid information was extracted from the input."
    
    st.session_state.messages.append({"role": "assistant", "content": ack})
    with st.chat_message("assistant", avatar=":material/robot_2:"):
        st.markdown(ack)


if st.button("Submit Data"):
    st.success("Your timetable data has been stored successfully!")
    if st.button("Proceed to Timetable"):
        st.switch_page("pages/Timetable.py")