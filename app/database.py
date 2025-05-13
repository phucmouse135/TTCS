from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

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

if __name__ == "__main__":
    init_db()
