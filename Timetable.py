import streamlit as st
from Version02.database import ScheduloDatabase
from typing import List, Dict

# --- Initialize the ScheduloDatabase instance ---
db = ScheduloDatabase()  
# Create the "Events" table if it does not exist.
db.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        academic_year TEXT,
        division TEXT,
        batch TEXT,
        time INTEGER,
        teacher_id TEXT,
        subject TEXT
    )
""")
db.conn.commit()

# --- Helper function to fetch timetable events from the database ---
def get_events() -> List[Dict]:
    query = "SELECT day, academic_year, division, batch, time, teacher_id, subject FROM Events"
    db.cursor.execute(query)
    rows = db.cursor.fetchall()
    events = []
    for row in rows:
        events.append({
            "day": row[0],
            "academic_year": row[1],
            "division": row[2],
            "batch": row[3],
            "time": row[4],
            "teacher_id": row[5],
            "subject": row[6]
        })
    return events

# --- Timetable Constants ---
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
ACADEMIC_YEARS = ["FE", "SE", "TE", "BE"]
DIVISIONS = {
    "FE": ["FE1", "FE2", "FE3"],
    "SE": ["SE1", "SE2", "SE3"],
    "TE": ["TE1", "TE2", "TE3"],
    "BE": ["BE1", "BE2", "BE3"]
}
BATCH = {
    "FE1": ["F1", "F2", "F3"],
    "FE2": ["F1", "F2", "F3"],
    "FE3": ["F1", "F2", "F3"],
    "SE1": ["S1", "S2", "S3"],
    "SE2": ["S1", "S2", "S3"],
    "SE3": ["S1", "S2", "S3"],
    "TE1": ["T1", "T2", "T3"],
    "TE2": ["T1", "T2", "T3"],
    "TE3": ["T1", "T2", "T3"],
    "BE1": ["B1", "B2", "B3"],
    "BE2": ["B1", "B2", "B3"],
    "BE3": ["B1", "B2", "B3"]
}

TEACHERS = [
    {"id": "T1", "name": "Dr. Smith", "subjects": ["Mathematics", "Physics"]},
    {"id": "T2", "name": "Prof. Johnson", "subjects": ["Computer Science"]},
    {"id": "T3", "name": "Dr. Brown", "subjects": ["Chemistry", "Biology"]},
]

TIME_SLOTS = list(range(6, 19))

# --- Streamlit Page Config: Wide layout and CSS modifications ---
st.set_page_config(page_title="Schedulo Timetable", page_icon="📅", layout="wide")
st.markdown(
    """
    <style>
    /* Increase width of the main container */
    .reportview-container .main .block-container {
        max-width: 100%;
        padding: 2rem 1rem;
    }
    /* Hide the pages sidebar */
    [data-testid="stSidebarNav"] { 
        display: none; 
    }
    /* Global font color set to white with a dark background */
    body, h1, h2, h3, h4, h5, h6, td, th, div {
        color: white;
    }
    .stApp {
        background-color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Function to render the timetable grid as HTML ---
def render_timetable(events: List[Dict]) -> str:
    grid_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Timetable Builder</title>
      <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
      <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/smoothness/jquery-ui.css">
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
      <style>
        body {{
            background-color: #333333;
            color: white;
            font-family: Arial, sans-serif;
        }}
        .container {{
            display: flex;
            gap: 20px;
        }}
        .timetable-container {{
            flex: 3;
        }}
        .teachers-panel {{
            flex: 1;
            background: #555555;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            top: 52px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #aaa;
            text-align: center;
            padding: 5px;
            min-width: 80px;
            height: 40px;
        }}
        th.fixed {{
            background-color: #ff6666;
        }}
        .draggable-item {{
            background-color: #28a99e;
            color: white;
            padding: 5px;
            margin: 5px 0;
            border-radius: 4px;
            cursor: move;
        }}
        .droppable-cell {{
            cursor: pointer;
            min-height: 30px;
        }}
        .droppable-cell.ui-droppable-hover {{
            background-color: #66cc66;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="timetable-container">
          <h1 style="text-align:center;">Timetable Builder</h1>
          <table id="timetable">
            <thead>
              <tr>
                <th class="fixed">Day</th>
                <th class="fixed">Academic Year</th>
                <th class="fixed">Division</th>
                <th class="fixed">Batch</th>"""
    for slot in TIME_SLOTS:
        grid_html += f"<th class='fixed'>{slot:02d}:00</th>"
    grid_html += "</tr></thead><tbody>"

    # Build rows for each day/academic year/division/batch combination
    for day in DAYS:
        first_row_of_day = True
        for ay in ACADEMIC_YEARS:
            first_row_of_ay = True
            for div in DIVISIONS[ay]:
                first_row_of_div = True
                for batch in BATCH[div]:
                    grid_html += "<tr>"
                    if first_row_of_day:
                        total_rows = sum(len(BATCH[d]) for ay in ACADEMIC_YEARS for d in DIVISIONS[ay])
                        grid_html += f"<td rowspan='{total_rows}'>{day}</td>"
                        first_row_of_day = False
                    if first_row_of_ay:
                        rows_ay = sum(len(BATCH[d]) for d in DIVISIONS[ay])
                        grid_html += f"<td rowspan='{rows_ay}'>{ay}</td>"
                        first_row_of_ay = False
                    if first_row_of_div:
                        grid_html += f"<td rowspan='{len(BATCH[div])}'>{div}</td>"
                        first_row_of_div = False
                    grid_html += f"<td>{batch}</td>"
                    for slot in TIME_SLOTS:
                        # Check if an event exists for this particular cell
                        cell_event = next((e for e in events if e["day"] == day and 
                                           e["academic_year"] == ay and 
                                           e["division"] == div and 
                                           e["batch"] == batch and 
                                           e["time"] == slot), None)
                        cell_content = ""
                        if cell_event:
                            teacher = next((t for t in TEACHERS if t["id"] == cell_event["teacher_id"]), None)
                            teacher_name = teacher["name"] if teacher else cell_event["teacher_id"]
                            cell_content = f"{teacher_name}<br>{cell_event['subject']}"
                        grid_html += f'''<td class="droppable-cell" data-day="{day}" data-ay="{ay}" 
                                        data-div="{div}" data-batch="{batch}" data-time="{slot}">{cell_content}</td>'''
                    grid_html += "</tr>"
    grid_html += """
            </tbody>
          </table>
          <br>
          <!-- Additional UI elements can be added here if needed -->
        </div>
        <div class="teachers-panel">
          <h3>Teachers & Subjects</h3>"""
    for teacher in TEACHERS:
        for subject in teacher["subjects"]:
            grid_html += f"""
              <div class="draggable-item" data-teacher-id="{teacher['id']}" data-subject="{subject}">
                <div>{teacher['name']}</div>
                <div style="font-size:12px;">{subject}</div>
              </div>
            """
    grid_html += """
        </div>
      </div>
      <script>
        // Make teacher items draggable
        $(".draggable-item").draggable({
            helper: 'clone',
            revert: 'invalid',
            zIndex: 100,
            containment: "document"
        });
        // Set droppable behavior for timetable cells
        $(".droppable-cell").droppable({
            accept: ".draggable-item",
            drop: function(event, ui) {
                var cell = $(this);
                var teacherData = ui.draggable.data();
                var teacherName = ui.draggable.text().split("\\n")[0];
                cell.html(teacherName + "<br>" + teacherData.subject);
                console.log("Dropped at:", cell.data());
                // Here you could add AJAX calls to update the database immediately
            }
        });
      </script>
    </body>
    </html>
    """
    return grid_html

# --- Main Application Entry Point ---
def main():
    st.title("Schedulo Timetable")
    events = get_events()  # Fetch events from the Events table
    html_code = render_timetable(events)
    st.components.v1.html(html_code, height=800, scrolling=True)

if __name__ == "__main__":
    main()
