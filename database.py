import sqlite3

class ScheduloDatabase:
    def __init__(self, db_name="schedulo.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS AcademicYears (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year_name TEXT UNIQUE
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Divisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year_name TEXT,
                division_name TEXT,
                FOREIGN KEY (year_name) REFERENCES AcademicYears(year_name),
                UNIQUE(year_name, division_name)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division_name TEXT,
                batch_name TEXT,
                FOREIGN KEY (division_name) REFERENCES Divisions(division_name),
                UNIQUE(division_name, batch_name)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Subjects (
                code TEXT PRIMARY KEY,
                name TEXT,
                year TEXT,
                type TEXT CHECK(type IN ('Lecture', 'Lab', 'Extra')),
                min_hours_per_week INTEGER
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Teachers (
                code TEXT PRIMARY KEY,
                name TEXT,
                max_workload INTEGER
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS TeacherSubjects (
                teacher_code TEXT,
                subject_code TEXT,
                FOREIGN KEY (teacher_code) REFERENCES Teachers(code),
                FOREIGN KEY (subject_code) REFERENCES Subjects(code),
                PRIMARY KEY (teacher_code, subject_code)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Venues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT CHECK(type IN ('Classroom', 'Lab'))
            )
        """)
        
        self.conn.commit()
    
    def insert_academic_year(self, year_name):
        try:
            self.cursor.execute("INSERT INTO AcademicYears (year_name) VALUES (?) ON CONFLICT(year_name) DO NOTHING", (year_name,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting academic year: {e}")
    
    def insert_division(self, year_name, division_name):
        try:
            self.cursor.execute("""
                INSERT INTO Divisions (year_name, division_name) 
                VALUES (?, ?) 
                ON CONFLICT(year_name, division_name) DO NOTHING
            """, (year_name, division_name))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting division: {e}")
    
    def insert_batch(self, division_name, batch_name):
        try:
            self.cursor.execute("""
                INSERT INTO Batches (division_name, batch_name) 
                VALUES (?, ?) 
                ON CONFLICT(division_name, batch_name) DO NOTHING
            """, (division_name, batch_name))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting batch: {e}")
    
    def insert_subject(self, code, name, year, type, min_hours_per_week):
        try:
            self.cursor.execute("""
                INSERT INTO Subjects (code, name, year, type, min_hours_per_week)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name=excluded.name,
                    year=excluded.year,
                    type=excluded.type,
                    min_hours_per_week=excluded.min_hours_per_week
            """, (code, name, year, type, min_hours_per_week))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting subject: {e}")
    
    def insert_teacher(self, code, name, max_workload):
        try:
            self.cursor.execute("""
                INSERT INTO Teachers (code, name, max_workload)
                VALUES (?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name=excluded.name,
                    max_workload=excluded.max_workload
            """, (code, name, max_workload))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting teacher: {e}")
    
    def insert_teacher_subject(self, teacher_code, subject_code):
        try:
            self.cursor.execute("""
                INSERT INTO TeacherSubjects (teacher_code, subject_code)
                VALUES (?, ?)
                ON CONFLICT(teacher_code, subject_code) DO NOTHING
            """, (teacher_code, subject_code))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting teacher subject: {e}")
    
    def insert_venue(self, name, type):
        try:
            self.cursor.execute("""
                INSERT INTO Venues (name, type)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    type=excluded.type
            """, (name, type))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting venue: {e}")
    
    def fetch_all(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching from {table_name}: {e}")
            return []
    
    def delete_record(self, table_name, column_name, value):
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = ?", (value,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting from {table_name}: {e}")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = ScheduloDatabase()
    print("Database initialized successfully with CRUD operations.")