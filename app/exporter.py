import os
import pandas as pd
import datetime
from sqlalchemy.orm import joinedload
from app.database import Session, Student, Schedule, Attendance

class AttendanceExporter:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_attendance_by_schedule(self, schedule_id):
        """Export attendance for a specific schedule to Excel"""
        session = Session()
        try:
            # Get the schedule with all attendances
            schedule = session.query(Schedule).options(
                joinedload(Schedule.attendances).joinedload(Attendance.student)
            ).filter_by(id=schedule_id).first()
            
            if not schedule:
                return False, f"Schedule with ID {schedule_id} not found"
            
            # Format date for filename
            date_str = schedule.date.strftime('%Y-%m-%d')
            file_name = f"diem_danh_{date_str}_{schedule.class_name}_{schedule.subject}.xlsx"
            file_path = os.path.join(self.output_dir, file_name)
            
            # Get all students (to include absent students)
            all_students = session.query(Student).all()
            
            # Create attendance data
            attendance_data = []
            for student in all_students:
                # Find attendance record for this student
                attendance = next(
                    (a for a in schedule.attendances if a.student_id == student.id), 
                    None
                )
                
                attendance_data.append({
                    'Tên học sinh': student.name,
                    'Mã học sinh': student.student_code,
                    'Trạng thái': 'x' if attendance and attendance.present else 'o'
                })
            
            # Create DataFrame and export to Excel
            df = pd.DataFrame(attendance_data)
            
            # Create a writer
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            
            # Write the data
            df.to_excel(writer, index=False, sheet_name='Điểm Danh')
            
            # Auto-fit column widths
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                # writer.sheets['Điểm Danh'].column_dimensions[chr(65 + col_idx)].width = column_width + 2
            
            # Save the file
            writer.close()
            
            return True, file_path
            
        except Exception as e:
            return False, f"Error exporting attendance: {str(e)}"
        finally:
            session.close()
    
    def export_attendance_by_date(self, date):
        """Export attendance for all schedules on a specific date"""
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        session = Session()
        try:
            # Find all schedules for this date
            schedules = session.query(Schedule).filter(
                Schedule.date >= datetime.datetime.combine(date, datetime.time.min),
                Schedule.date <= datetime.datetime.combine(date, datetime.time.max)
            ).all()
            
            if not schedules:
                return False, f"No schedules found for date {date}"
            
            # Export each schedule
            results = []
            for schedule in schedules:
                success, result = self.export_attendance_by_schedule(schedule.id)
                if success:
                    results.append(result)
            
            if results:
                return True, results
            else:
                return False, "Failed to export any attendance records"
                
        except Exception as e:
            return False, f"Error exporting attendance: {str(e)}"
        finally:
            session.close()
    
    def export_absent_students(self, start_date=None, end_date=None):
        """Export a list of students who were absent during the specified period"""
        if start_date is None:
            # Default to last 30 days
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=30)
        
        if end_date is None:
            end_date = datetime.datetime.now().date()
            
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        session = Session()
        try:
            # Get all schedules in the date range
            schedules = session.query(Schedule).filter(
                Schedule.date >= datetime.datetime.combine(start_date, datetime.time.min),
                Schedule.date <= datetime.datetime.combine(end_date, datetime.time.max)
            ).options(joinedload(Schedule.attendances)).all()
            
            if not schedules:
                return False, f"No schedules found between {start_date} and {end_date}"
            
            # Get all students
            students = session.query(Student).all()
            
            # Track absent students by schedule
            absent_data = []
            
            for schedule in schedules:
                for student in students:
                    # Find attendance record for this student in this schedule
                    attendance = next(
                        (a for a in schedule.attendances if a.student_id == student.id), 
                        None
                    )
                    
                    # If no attendance record or not present, student was absent
                    if not attendance or not attendance.present:
                        absent_data.append({
                            'Tên học sinh': student.name,
                            'Mã học sinh': student.student_code,
                            'Lớp': schedule.class_name,
                            'Môn học': schedule.subject,
                            'Ngày': schedule.date.strftime('%Y-%m-%d'),
                            'Giờ bắt đầu': schedule.start_time,
                            'Giờ kết thúc': schedule.end_time
                        })
            
            if not absent_data:
                return False, "No absent records found"
                
            # Create DataFrame and export to Excel
            df = pd.DataFrame(absent_data)
            
            # Format dates for filename
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            file_name = f"vang_mat_{start_str}_to_{end_str}.xlsx"
            file_path = os.path.join(self.output_dir, file_name)
            
            # Create a writer
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            
            # Write the data
            df.to_excel(writer, index=False, sheet_name='Vắng Mặt')
            
            # Save the file
            writer.close()
            
            return True, file_path
            
        except Exception as e:
            return False, f"Error exporting absent students: {str(e)}"
        finally:
            session.close()
