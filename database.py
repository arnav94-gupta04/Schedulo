import sqlite3

class ScheduloDatabase:
    def __init__(self, db_file="schedulo.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # So we can access columns by name
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        """)
        # AcademicYears table
        c.execute("""
            CREATE TABLE IF NOT EXISTS AcademicYears (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT UNIQUE
            )
        """)
        # Divisions table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Divisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT,
                division TEXT,
                UNIQUE(year, division)
            )
        """)
        # Batches table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division TEXT,
                batch TEXT,
                UNIQUE(division, batch)
            )
        """)
        # Subjects table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT,
                year TEXT,
                type TEXT,
                min_hours_per_week INTEGER
            )
        """)
        # Teachers table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT,
                max_workload INTEGER
            )
        """)
        # TeacherSubjects mapping table
        c.execute("""
            CREATE TABLE IF NOT EXISTS TeacherSubjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_code TEXT,
                subject_code TEXT,
                UNIQUE(teacher_code, subject_code)
            )
        """)
        # Venues table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Venues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT
            )
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # --- User-related methods ---
    def insert_user(self, first_name, last_name, email, password):
        c = self.conn.cursor()
        try:
            c.execute(
                "INSERT INTO Users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, email, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
        return c.fetchone()

    def get_user_by_email(self, email):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Users WHERE email = ?", (email,))
        return c.fetchone()

    # --- Academic Years ---
    def insert_academic_year(self, year):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO AcademicYears (year) VALUES (?)", (year,))
        self.conn.commit()

    def get_academic_years(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM AcademicYears")
        return c.fetchall()

    # --- Divisions ---
    def insert_division(self, year, division):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO Divisions (year, division) VALUES (?, ?)", (year, division))
        self.conn.commit()

    def get_divisions(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Divisions")
        return c.fetchall()

    # --- Batches ---
    def insert_batch(self, division, batch):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO Batches (division, batch) VALUES (?, ?)", (division, batch))
        self.conn.commit()

    def get_batches(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Batches")
        return c.fetchall()

    # --- Subjects ---
    def insert_subject(self, code, name, year, type, min_hours_per_week):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO Subjects (code, name, year, type, min_hours_per_week) VALUES (?, ?, ?, ?, ?)",
            (code, name, year, type, min_hours_per_week)
        )
        self.conn.commit()

    def get_subjects(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Subjects")
        return c.fetchall()

    def update_subject(self, code, name, year, type, min_hours_per_week):
        c = self.conn.cursor()
        c.execute("""
            UPDATE Subjects
            SET name = ?, year = ?, type = ?, min_hours_per_week = ?
            WHERE code = ?
        """, (name, year, type, min_hours_per_week, code))
        self.conn.commit()

    def delete_subject(self, code):
        c = self.conn.cursor()
        c.execute("DELETE FROM Subjects WHERE code = ?", (code,))
        self.conn.commit()

    # --- Teachers ---
    def insert_teacher(self, code, name, max_workload):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO Teachers (code, name, max_workload) VALUES (?, ?, ?)",
            (code, name, max_workload)
        )
        self.conn.commit()

    def get_teachers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Teachers")
        return c.fetchall()

    # --- TeacherSubjects mapping ---
    def insert_teacher_subject(self, teacher_code, subject_code):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO TeacherSubjects (teacher_code, subject_code) VALUES (?, ?)",
            (teacher_code, subject_code)
        )
        self.conn.commit()

    def get_teacher_subjects(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM TeacherSubjects")
        return c.fetchall()

    # --- Venues ---
    def insert_venue(self, name, type):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO Venues (name, type) VALUES (?, ?)", (name, type))
        self.conn.commit()

    def get_venues(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Venues")
        return c.fetchall()

if __name__ == "__main__":
    db = ScheduloDatabase()
    print("Database initialized and tables created.")
    db.close()
