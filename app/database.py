from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import sqlite3

# Create the database engine
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')
engine = create_engine(f'sqlite:///{DB_PATH}')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    student_code = Column(String, unique=True, nullable=False)
    image_path = Column(String)
    embedding_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    attendances = relationship("Attendance", back_populates="student")
    
    def __repr__(self):
        return f"<Student(name='{self.name}', student_code='{self.student_code}')>"

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    class_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    
    attendances = relationship("Attendance", back_populates="schedule")
    
    def __repr__(self):
        return f"<Schedule(date='{self.date}', class_name='{self.class_name}', subject='{self.subject}')>"

class Attendance(Base):
    __tablename__ = 'attendances'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    present = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    student = relationship("Student", back_populates="attendances")
    schedule = relationship("Schedule", back_populates="attendances")
    
    def __repr__(self):
        return f"<Attendance(student_id='{self.student_id}', schedule_id='{self.schedule_id}', present='{self.present}')>"

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_class_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
                UNIQUE(student_id, class_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS class_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room TEXT,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()

    # Class Management Methods
    def add_class(self, name, description=""):
        self.cursor.execute('INSERT INTO classes (name, description) VALUES (?, ?)',
                           (name, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_classes(self):
        self.cursor.execute('SELECT * FROM classes')
        return self.cursor.fetchall()

    def get_class_by_id(self, class_id):
        self.cursor.execute('SELECT * FROM classes WHERE id = ?', (class_id,))
        return self.cursor.fetchone()

    def update_class(self, class_id, name, description):
        self.cursor.execute('UPDATE classes SET name = ?, description = ? WHERE id = ?',
                           (name, description, class_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_class(self, class_id):
        self.cursor.execute('DELETE FROM classes WHERE id = ?', (class_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Student-Class Assignment Methods
    def assign_student_to_class(self, student_id, class_id):
        try:
            self.cursor.execute('INSERT INTO student_class_assignments (student_id, class_id) VALUES (?, ?)',
                               (student_id, class_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Student already assigned to this class

    def remove_student_from_class(self, student_id, class_id):
        self.cursor.execute('DELETE FROM student_class_assignments WHERE student_id = ? AND class_id = ?',
                           (student_id, class_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_students_in_class(self, class_id):
        self.cursor.execute('''
            SELECT s.* FROM students s
            JOIN student_class_assignments sca ON s.id = sca.student_id
            WHERE sca.class_id = ?
        ''', (class_id,))
        return self.cursor.fetchall()

    def get_classes_for_student(self, student_id):
        self.cursor.execute('''
            SELECT c.* FROM classes c
            JOIN student_class_assignments sca ON c.id = sca.class_id
            WHERE sca.student_id = ?
        ''', (student_id,))
        return self.cursor.fetchall()

    # Class Schedule Methods
    def add_class_schedule(self, class_id, day_of_week, start_time, end_time, room=""):
        self.cursor.execute('''
            INSERT INTO class_schedules (class_id, day_of_week, start_time, end_time, room)
            VALUES (?, ?, ?, ?, ?)
        ''', (class_id, day_of_week, start_time, end_time, room))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_schedules_for_class(self, class_id):
        self.cursor.execute('SELECT * FROM class_schedules WHERE class_id = ?', (class_id,))
        return self.cursor.fetchall()

    def update_class_schedule(self, schedule_id, day_of_week, start_time, end_time, room):
        self.cursor.execute('''
            UPDATE class_schedules 
            SET day_of_week = ?, start_time = ?, end_time = ?, room = ?
            WHERE id = ?
        ''', (day_of_week, start_time, end_time, room, schedule_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_class_schedule(self, schedule_id):
        self.cursor.execute('DELETE FROM class_schedules WHERE id = ?', (schedule_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_student_id_by_code(self, student_code):
        """Get student ID from student_code"""
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM students WHERE student_code = ?", (student_code,))
        row = cur.fetchone()
        return row[0] if row else None

if __name__ == "__main__":
    init_db()
