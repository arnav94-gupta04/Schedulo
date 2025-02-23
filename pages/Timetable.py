import streamlit as st
import json
import uuid
#from db import TimetableDB
from typing import List, Dict, Optional

# Constants
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

# Initialize database in session state
if 'db' not in st.session_state:
    st.session_state.db = TimetableDB()

# Set page to maximum width for table 
st.set_page_config(layout="wide")

#Remove this part to remove the Title + Image
with st.container():
    st.image(r"C:\Users\YASMEEN\Downloads\Pretty.png", width=100)
    st.markdown("<h3 style='padding: 0px; margin-bottom: 10px;' >SchedulO</h3>", unsafe_allow_html=True)
    
# Remove default hamburger menu
st.markdown(
    """
    <style>
    .stAppDeployButton{  
        visibility: Hidden;
    }
    .stMainMenu{   
        visibility: Hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def render_timetable(events: List[Dict]):
    grid_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Timetable Builder</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/smoothness/jquery-ui.css">
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        <style>
        .container {{
            display: flex;
            gap: 20px;
        }}
        .timetable-container {{
            flex: 3;
        }}
        .teachers-panel {{
            flex: 1;
            background: #f5f5f5;      
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            right: 0px;
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
            position: relative;
            min-width: 80px;
            height: 20px;
        }}
        th.fixed {{
            background-color: #ffcccc;
        }}
        .draggable-item {{
            background-color: #28a99e;
            color: white;
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            cursor: move;
            user-select: none;
        }}
        .draggable-item:hover {{
            background-color: #4fb9af;
        }}
        .droppable-cell {{
            cursor: pointer;
            min-height: 30px;
        }}
        .droppable-cell.ui-droppable-hover {{
            background-color: #e6ffe6;
        }}
        .teacher-subject {{
            font-size: 12px;
            color: #e5e5e5;
            margin-top: 3px;
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
                            <th class="fixed">Batch</th>                            
    """
   
    for slot in TIME_SLOTS:
        grid_html += f"<th class='fixed'>{slot:02d}:00</th>"
    grid_html += "</tr></thead><tbody>"

    # Calculate rowspans for merged cells
    for day in DAYS:
        first_row_of_day = True
        for ay in ACADEMIC_YEARS:
            first_row_of_ay = True
            divisions = DIVISIONS[ay]
            
            for div in divisions:
                first_row_of_div = True
                batches = BATCH[div]
                
                for batch in batches:
                    grid_html += "<tr>"
                    
                    # Add day cell only on first row with proper rowspan
                    if first_row_of_day:
                        total_rows_per_day = sum(len(DIVISIONS[ay]) * len(BATCH[div]) for ay in ACADEMIC_YEARS)
                        grid_html += f"<td rowspan='{total_rows_per_day}'>{day}</td>"
                        first_row_of_day = False
                    
                    # Add academic year cell only on its first division row
                    if first_row_of_ay:
                        rows_for_ay = sum(len(BATCH[d]) for d in DIVISIONS[ay])
                        grid_html += f"<td rowspan='{rows_for_ay}'>{ay}</td>"
                        first_row_of_ay = False
                    
                    # Add division cell only on its first batch row
                    if first_row_of_div:
                        grid_html += f"<td rowspan='{len(BATCH[div])}'>{div}</td>"
                        first_row_of_div = False
                    
                    # Add batch cell
                    grid_html += f"<td>{batch}</td>"
                    
                    # Add time slot cells
                    for slot in TIME_SLOTS:
                        grid_html += f'''<td class="droppable-cell" 
                            data-day="{day}" 
                            data-ay="{ay}" 
                            data-div="{div}" 
                            data-batch="{batch}"
                            data-time="{slot}"></td>'''
                    
                    grid_html += "</tr>"

    # Rest of the HTML (teachers panel and JavaScript) remains the same
    grid_html += """
                </tbody>
                </table>
            </div>
            <div class="teachers-panel">
                <h3>Teachers & Subjects</h3>
                <div id="teachers-list">
    """
    
    # Add teacher items
    for teacher in TEACHERS:
        for subject in teacher["subjects"]:
            grid_html += f"""
                <div class="draggable-item" 
                     data-teacher-id="{teacher['id']}" 
                     data-teacher-name="{teacher['name']}"
                     data-subject="{subject}">
                    <div>{teacher['name']}</div>
                    <div class="teacher-subject">{subject}</div>
                </div>
            """
    
    grid_html += """
                </div>
            </div>
        </div>
        <script>
        $(document).ready(function() {
            function initDraggable(element) {
                $(element).draggable({
                    helper: 'clone',
                    revert: 'invalid',
                    zIndex: 100,
                    containment: "document"
                });
            }

            $('.draggable-item').each(function() {
                initDraggable(this);
            });

            $('.droppable-cell').droppable({
                accept: '.draggable-item',
                drop: function(event, ui) {
                    const cell = $(this);
                    const teacherData = ui.draggable.data();
                    
                    if (ui.draggable.parent().is('#teachers-list')) {
                        const droppedItem = $('<div>')
                            .addClass('draggable-item')
                            .css({
                                'position': 'relative',
                                'top': 'auto',
                                'left': 'auto'
                            })
                            .html(`
                                <div>${teacherData.teacherName}</div>
                                <div class="teacher-subject">${teacherData.subject}</div>
                            `);
                        
                        cell.empty().append(droppedItem);
                        initDraggable(droppedItem);
                    } else {
                        const item = ui.draggable;
                        cell.empty().append(item);
                        item.css({
                            'position': 'relative',
                            'top': 'auto',
                            'left': 'auto'
                        });
                    }
                    
                    const eventData = {
                        day: cell.data('day'),
                        academic_year: cell.data('ay'),
                        division: cell.data('div'),
                        batch: cell.data('batch'),
                        time: cell.data('time'),
                        teacher_id: teacherData.teacherId,
                        subject: teacherData.subject
                    };
                    
                    console.log('Dropped event:', eventData);
                }
            });
        });
        </script>
    </body>
    </html>
    """

    st.components.v1.html(grid_html, height=800, scrolling=True)

def main():
    events = st.session_state.db.get_events()
    render_timetable(events)

if __name__ == "__main__":
    main()