import sqlite3

def print_table_contents(cursor, table_name, header):
    print(f"--- {header} ({table_name}) ---")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("No records found.")
    print("-" * 40)

def view_database_contents():
    conn = sqlite3.connect("schedulo.db")
    cursor = conn.cursor()
    
    tables = [
        ("AcademicYears", "Academic Years"),
        ("Divisions", "Divisions"),
        ("Batches", "Batches"),
        ("Subjects", "Subjects"),
        ("Teachers", "Teachers"),
        ("TeacherSubjects", "Teacher-Subject Assignments"),
        ("Venues", "Venues")
    ]
    
    for table, header in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            print_table_contents(cursor, table, header)
        except Exception as e:
            print(f"Error reading table {table}: {e}")
    
    conn.close()

if __name__ == "__main__":
    view_database_contents()
