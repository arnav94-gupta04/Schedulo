from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

# Sample data - in a real application, this would come from a database
resources = [
    {"id": "a", "title": "Room A", "group": "Meeting Rooms"},
    {"id": "b", "title": "Room B", "group": "Meeting Rooms"},
    {"id": "c", "title": "Auditorium", "group": "Conference Spaces"},
    {"id": "d", "title": "Main Hall", "group": "Conference Spaces"},
    {"id": "e", "title": "Workshop 1", "group": "Training Rooms"},
    {"id": "f", "title": "Workshop 2", "group": "Training Rooms"},
]

events = [
    {"id": "1", "resourceId": "a", "title": "Team Meeting", "start": 9, "end": 11, "color": "#3788d8"},
    {"id": "2", "resourceId": "b", "title": "Client Call", "start": 10, "end": 11, "color": "#8e24aa"},
    {"id": "3", "resourceId": "c", "title": "Company Presentation", "start": 13, "end": 15, "color": "#e67c73"},
    {"id": "4", "resourceId": "d", "title": "Conference", "start": 9, "end": 17, "color": "#33b679"},
    {"id": "5", "resourceId": "e", "title": "Python Training", "start": 10, "end": 12, "color": "#f6bf26"},
    {"id": "6", "resourceId": "f", "title": "React Workshop", "start": 14, "end": 16, "color": "#039be5"},
]

# Group resources by group field
def group_resources(resources):
    grouped = {}
    for resource in resources:
        group_name = resource.get('group', 'Ungrouped')
        if group_name not in grouped:
            grouped[group_name] = []
        grouped[group_name].append(resource)
    return grouped

# Get time slots based on start and end times
def get_time_slots(start_time=8, end_time=18):
    return list(range(start_time, end_time + 1))

@app.route('/')
def index():
    selected_date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    time_start = int(request.args.get('time_start', 8))
    time_end = int(request.args.get('time_end', 18))
    
    # Prepare data for the template
    grouped_resources = group_resources(resources)
    time_slots = get_time_slots(time_start, time_end)
    
    return render_template(
        'index.html', 
        grouped_resources=grouped_resources, 
        events=events, 
        time_slots=time_slots,
        selected_date=selected_date,
        time_start=time_start,
        time_end=time_end
    )

@app.route('/calendar')
def calendar_partial():
    selected_date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    time_start = int(request.args.get('time_start', 8))
    time_end = int(request.args.get('time_end', 18))
    
    # Prepare data for the template
    grouped_resources = group_resources(resources)
    time_slots = get_time_slots(time_start, time_end)
    
    return render_template(
        'calendar_partial.html', 
        grouped_resources=grouped_resources, 
        events=events, 
        time_slots=time_slots,
        selected_date=selected_date,
        time_start=time_start,
        time_end=time_end
    )

# API routes for CRUD operations if needed
@app.route('/api/events', methods=['POST'])
def create_event():
    new_event = request.json
    
    # Generate a new ID (in a real app, this would be handled by the database)
    existing_ids = [int(event["id"]) for event in events if event["id"].isdigit()]
    new_id = str(max(existing_ids) + 1) if existing_ids else "1"
    
    new_event["id"] = new_id
    events.append(new_event)
    
    return jsonify(new_event), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)