import sys
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
                             QDateEdit, QTimeEdit, QMessageBox, QComboBox, QCalendarWidget, QDialog,
                             QHeaderView, QRadioButton, QButtonGroup, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np
from PIL import Image, ImageQt

from app.database import Session, Student, Schedule, Attendance, init_db
from app.face_recognition import FaceRecognition
from app.exporter import AttendanceExporter
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ Thống Điểm Danh Bằng Nhận Diện Khuôn Mặt")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize database if not exists
        init_db()
        
        # Initialize face recognition
        self.face_recognition = FaceRecognition()
        
        # Initialize exporter
        self.exporter = AttendanceExporter()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize extra buttons
        self.initialize_extra_buttons()
    
    def setup_ui(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create each tab
        self.create_students_tab()
        self.create_schedules_tab()
        self.create_attendance_tab()
        self.create_reports_tab()
    
    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Student form
        form_group = QGroupBox("Thêm Học Sinh Mới")
        form_layout = QFormLayout()
        
        self.student_name_input = QLineEdit()
        self.student_code_input = QLineEdit()
        
        form_layout.addRow("Tên Học Sinh:", self.student_name_input)
        form_layout.addRow("Mã Học Sinh:", self.student_code_input)
        
        # Image selection options
        img_options_group = QGroupBox("Ảnh Khuôn Mặt")
        img_options_layout = QVBoxLayout()
        
        option_layout = QHBoxLayout()
        
        self.img_option_group = QButtonGroup()
        self.radio_upload = QRadioButton("Tải lên ảnh")
        self.radio_camera = QRadioButton("Chụp từ camera")
        self.img_option_group.addButton(self.radio_upload)
        self.img_option_group.addButton(self.radio_camera)
        self.radio_upload.setChecked(True)
        
        option_layout.addWidget(self.radio_upload)
        option_layout.addWidget(self.radio_camera)
        
        img_options_layout.addLayout(option_layout)
        
        # Upload button
        self.upload_layout = QHBoxLayout()
        self.img_path_input = QLineEdit()
        self.img_path_input.setReadOnly(True)
        self.browse_btn = QPushButton("Chọn Ảnh")
        self.browse_btn.clicked.connect(self.browse_image)
        
        self.upload_layout.addWidget(self.img_path_input)
        self.upload_layout.addWidget(self.browse_btn)
        
        img_options_layout.addLayout(self.upload_layout)
        
        # Camera button (initially hidden)
        self.camera_btn = QPushButton("Chụp Ảnh từ Camera")
        self.camera_btn.clicked.connect(self.capture_from_camera)
        img_options_layout.addWidget(self.camera_btn)
        self.camera_btn.hide()
        
        # Connect radio buttons
        self.radio_upload.toggled.connect(self.toggle_image_option)
        self.radio_camera.toggled.connect(self.toggle_image_option)
        
        img_options_group.setLayout(img_options_layout)
        
        # Preview image
        self.preview_label = QLabel("Xem trước ảnh")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        
        # Add student button
        self.add_student_btn = QPushButton("Thêm Học Sinh")
        self.add_student_btn.clicked.connect(self.add_student)
        
        # Set form layout
        form_group.setLayout(form_layout)
        
        # Add widgets to layout
        layout.addWidget(form_group)
        layout.addWidget(img_options_group)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.add_student_btn)
        
        # Students list
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(3)
        self.students_table.setHorizontalHeaderLabels(["Tên Học Sinh", "Mã Học Sinh", "Hành Động"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("Danh Sách Học Sinh"))
        layout.addWidget(self.students_table)
        
        # Load students
        self.load_students()
        
        self.tabs.addTab(tab, "Quản Lý Học Sinh")
    
    def create_schedules_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Schedule form
        form_group = QGroupBox("Thêm Lịch Học Mới")
        form_layout = QFormLayout()
        
        self.schedule_date = QDateEdit()
        self.schedule_date.setCalendarPopup(True)
        self.schedule_date.setDate(QDate.currentDate())
        
        self.class_name_input = QLineEdit()
        self.subject_input = QLineEdit()
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(7, 30))
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(9, 0))
        
        form_layout.addRow("Ngày:", self.schedule_date)
        form_layout.addRow("Lớp:", self.class_name_input)
        form_layout.addRow("Môn học:", self.subject_input)
        form_layout.addRow("Giờ bắt đầu:", self.start_time)
        form_layout.addRow("Giờ kết thúc:", self.end_time)
        
        form_group.setLayout(form_layout)
        
        # Add schedule button
        self.add_schedule_btn = QPushButton("Thêm Lịch Học")
        self.add_schedule_btn.clicked.connect(self.add_schedule)
        
        # Add widgets to layout
        layout.addWidget(form_group)
        layout.addWidget(self.add_schedule_btn)
        
        # Schedules list
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels(
            ["Ngày", "Lớp", "Môn Học", "Bắt Đầu", "Kết Thúc", "Hành Động"]
        )
        self.schedules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("Danh Sách Lịch Học"))
        layout.addWidget(self.schedules_table)
        
        # Load schedules
        self.load_schedules()
        
        self.tabs.addTab(tab, "Quản Lý Lịch Học")
    
    def create_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Select schedule
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Chọn lịch học:"))
        
        self.schedule_combo = QComboBox()
        form_layout.addWidget(self.schedule_combo)
        
        self.refresh_schedules_btn = QPushButton("Làm Mới")
        self.refresh_schedules_btn.clicked.connect(self.load_schedule_combo)
        form_layout.addWidget(self.refresh_schedules_btn)
        
        layout.addLayout(form_layout)
        
        # Start attendance button
        self.start_attendance_btn = QPushButton("Bắt Đầu Điểm Danh")
        self.start_attendance_btn.clicked.connect(self.start_attendance)
        layout.addWidget(self.start_attendance_btn)
        
        # Export button
        self.export_btn = QPushButton("Xuất File Excel")
        self.export_btn.clicked.connect(self.export_attendance)
        layout.addWidget(self.export_btn)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(3)
        self.attendance_table.setHorizontalHeaderLabels(["Tên Học Sinh", "Mã Học Sinh", "Có Mặt"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("Kết Quả Điểm Danh"))
        layout.addWidget(self.attendance_table)
        
        # Load schedules into combo
        self.load_schedule_combo()
        
        self.tabs.addTab(tab, "Điểm Danh")
    
    def create_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Date range selection
        date_range_group = QGroupBox("Chọn Khoảng Thời Gian")
        date_range_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        
        date_range_layout.addWidget(QLabel("Từ:"))
        date_range_layout.addWidget(self.start_date)
        date_range_layout.addWidget(QLabel("Đến:"))
        date_range_layout.addWidget(self.end_date)
        
        date_range_group.setLayout(date_range_layout)
        layout.addWidget(date_range_group)
        
        # Generate reports buttons
        buttons_layout = QHBoxLayout()
        
        self.export_absent_btn = QPushButton("Xuất Danh Sách Vắng Mặt")
        self.export_absent_btn.clicked.connect(self.export_absent)
        buttons_layout.addWidget(self.export_absent_btn)
        
        layout.addLayout(buttons_layout)
        
        # Reports table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels(
            ["Học Sinh", "Lớp", "Ngày", "Trạng Thái"]
        )
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("Báo Cáo Điểm Danh"))
        layout.addWidget(self.reports_table)
        
        self.tabs.addTab(tab, "Báo Cáo")
    
    def toggle_image_option(self):
        if self.radio_upload.isChecked():
            self.upload_layout.parentWidget().layout().setEnabled(True)
            self.img_path_input.show()
            self.browse_btn.show()
            self.camera_btn.hide()
        else:
            self.upload_layout.parentWidget().layout().setEnabled(False)
            self.img_path_input.hide()
            self.browse_btn.hide()
            self.camera_btn.show()
    
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn Ảnh", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.img_path_input.setText(file_path)
            self.show_preview(file_path)
    
    def show_preview(self, img_path):
        pixmap = QPixmap(img_path)
        
        # Scale the pixmap while preserving the aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(), 
            self.preview_label.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
    
    def capture_from_camera(self):
        """Capture face images from camera for student registration"""
        try:
            # Use QInputDialog for reliable input
            from PyQt5.QtWidgets import QMessageBox, QInputDialog
            
            # Get student ID and name
            student_code, ok1 = QInputDialog.getText(self, "Student Registration", "Enter Student ID/Code:")
            if not ok1 or not student_code.strip():
                return
                
            name, ok2 = QInputDialog.getText(self, "Student Registration", "Enter Student Name:")
            if not ok2 or not name.strip():
                return
            
            # Show preparation message
            QMessageBox.information(
                self, 
                "Camera Capture", 
                "The camera will open now. Please look at the camera and move your face slightly.\n\n"
                "Press ESC to cancel anytime."
            )
            
            # Direct call to face collection method with proper error handling
            try:
                # Create a simple progress dialog
                from PyQt5.QtWidgets import QProgressDialog
                from PyQt5.QtCore import Qt
                
                progress = QProgressDialog("Collecting face images...", "Cancel", 0, 100, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(10)
                
                # Call the collection method
                success, message = self.face_recognition.collect_faces_from_camera(student_code, name)
                
                # Close progress dialog
                progress.setValue(100)
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    # Refresh student list
                    self.load_students()  # Use the most common method name
                else:
                    QMessageBox.warning(self, "Warning", message)
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error collecting faces: {e}\n{error_details}")
                QMessageBox.critical(self, "Error", f"Face collection failed: {str(e)}")
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            error_msg = f"Camera capture error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def show_success_message(self, message):
        """Show success message (called from thread)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", message)
        self.refresh_student_list()

    def show_error_message(self, message):
        """Show error message (called from thread)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)

    def refresh_student_list(self):
        """Refresh student list in UI"""
        try:
            # Try different possible method names for refreshing the student list
            if hasattr(self, 'load_students'):
                self.load_students()
            elif hasattr(self, 'refresh_students'):
                self.refresh_students()
            elif hasattr(self, 'update_student_list'):
                self.update_student_list()
            print("Student list refreshed")
        except Exception as e:
            print(f"Error refreshing student list: {e}")

    def add_student(self):
        if self.radio_upload.isChecked():
            # Get input values
            student_name = self.student_name_input.text().strip()
            student_code = self.student_code_input.text().strip()
            img_path = self.img_path_input.text().strip()
            
            if not student_name or not student_code or not img_path:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin")
                return
            
            # Check if student code already exists
            session = Session()
            try:
                if session.query(Student).filter_by(student_code=student_code).first():
                    QMessageBox.warning(self, "Lỗi", f"Mã học sinh {student_code} đã tồn tại")
                    return
            finally:
                session.close()
            
            # Directory to save student images
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'data', 'student_images', student_code)
            os.makedirs(save_dir, exist_ok=True)
            
            # Copy image to student directory
            import shutil
            filename = os.path.basename(img_path)
            new_path = os.path.join(save_dir, filename)
            shutil.copy2(img_path, new_path)
            
            # Add student to face recognition system
            success, message = self.face_recognition.add_student(student_code, student_name, new_path)
            
            if success:
                # Add student to database
                session = Session()
                try:
                    student = Student(
                        name=student_name,
                        student_code=student_code,
                        image_path=new_path
                    )
                    session.add(student)
                    session.commit()
                    
                    QMessageBox.information(self, "Thành công", f"Đã thêm học sinh {student_name}")
                    
                    # Reload students
                    self.load_students()
                    
                    # Clear form
                    self.student_name_input.clear()
                    self.student_code_input.clear()
                    self.img_path_input.clear()
                    self.preview_label.clear()
                    self.preview_label.setText("Xem trước ảnh")
                    
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Lỗi", f"Không thể thêm học sinh: {str(e)}")
                finally:
                    session.close()
            else:
                QMessageBox.critical(self, "Lỗi", message)
        else:
            # If camera option is selected, use capture_from_camera method
            self.capture_from_camera()
    
    def load_students(self):
        """Load students from the database into the table"""
        try:
            # Find the student table widget
            if hasattr(self, 'students_table'):
                table_widget = self.students_table
            elif hasattr(self, 'tableWidget'):
                table_widget = self.tableWidget
            else:
                print("Could not find student table widget")
                return
            
            # Clear the table
            table_widget.setRowCount(0)
            
            # Get students from database
            students = self.face_recognition.df
            
            if len(students) == 0:
                print("No students in database")
                return
            
            # Set table properties
            table_widget.setRowCount(len(students))
            
            # Populate table with student data
            from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
            from PyQt5.QtGui import QFont
            
            # Create a font that supports Vietnamese characters
            vietnamese_font = QFont()
            vietnamese_font.setFamily("Arial") # A font that supports Vietnamese
            vietnamese_font.setPointSize(10)
            
            for i, (_, student) in enumerate(students.iterrows()):
                # Convert all values to strings to avoid type errors
                student_code = str(student['student_code']).strip()
                name = str(student['name']).strip()
                
                # Name (column 0) - "Tên Học Sinh"
                name_item = QTableWidgetItem(name)
                name_item.setFont(vietnamese_font) # Set the font for Vietnamese display
                table_widget.setItem(i, 0, name_item)
                
                # Student code (column 1) - "Mã Học Sinh"
                code_item = QTableWidgetItem(student_code)
                table_widget.setItem(i, 1, code_item)
                
                # Add Delete button (column 2) - "Hành Động"
                delete_button = QPushButton("Xóa")
                delete_button.setStyleSheet("background-color: #ff6b6b; color: white;")
                delete_button.clicked.connect(lambda checked, code=student_code: self.delete_student_by_id(code))
                table_widget.setCellWidget(i, 2, delete_button)
            
            print(f"Loaded {len(students)} students into table")
        except Exception as e:
            import traceback
            print(f"Error loading students: {e}\n{traceback.format_exc()}")

    def delete_student_by_id(self, student_code):
        """Delete a student by their ID"""
        try:
            # Debug information
            print(f"Deleting student with code: {student_code}")
            
            # Confirm deletion
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 
                "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa học sinh có mã {student_code}?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Delete the student
                success, message = self.face_recognition.delete_student(student_code)
                
                if success:
                    QMessageBox.information(self, "Thành công", message)
                    # Refresh the student list
                    self.load_students()
                else:
                    QMessageBox.critical(self, "Lỗi", message)
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error deleting student by ID: {e}\n{error_details}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa học sinh: {str(e)}")

    def delete_student(self, student_id):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xoá học sinh này?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            session = Session()
            try:
                student = session.query(Student).filter_by(id=student_id).first()
                
                if student:
                    # Remove from face recognition system (remove embedding)
                    if student.student_code in self.face_recognition.embeddings:
                        del self.face_recognition.embeddings[student.student_code]
                        self.face_recognition.save_embeddings()
                    
                    # Delete from database
                    session.delete(student)
                    session.commit()
                    
                    QMessageBox.information(self, "Thành công", "Đã xoá học sinh")
                    
                    # Reload students
                    self.load_students()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy học sinh")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xoá học sinh: {str(e)}")
            finally:
                session.close()
    
    def add_schedule(self):
        # Get input values
        date = self.schedule_date.date().toPyDate()
        class_name = self.class_name_input.text().strip()
        subject = self.subject_input.text().strip()
        start_time = self.start_time.time().toString("HH:mm")
        end_time = self.end_time.time().toString("HH:mm")
        
        if not class_name or not subject:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin")
            return
        
        # Add schedule to database
        session = Session()
        try:
            schedule = Schedule(
                date=date,
                class_name=class_name,
                subject=subject,
                start_time=start_time,
                end_time=end_time
            )
            session.add(schedule)
            session.commit()
            
            QMessageBox.information(self, "Thành công", f"Đã thêm lịch học cho lớp {class_name}")
            
            # Reload schedules
            self.load_schedules()
            self.load_schedule_combo()
            
            # Clear form
            self.class_name_input.clear()
            self.subject_input.clear()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm lịch học: {str(e)}")
        finally:
            session.close()
    
    def load_schedules(self):
        session = Session()
        try:
            schedules = session.query(Schedule).all()
            
            self.schedules_table.setRowCount(len(schedules))
            
            for i, schedule in enumerate(schedules):
                self.schedules_table.setItem(i, 0, QTableWidgetItem(schedule.date.strftime('%Y-%m-%d')))
                self.schedules_table.setItem(i, 1, QTableWidgetItem(schedule.class_name))
                self.schedules_table.setItem(i, 2, QTableWidgetItem(schedule.subject))
                self.schedules_table.setItem(i, 3, QTableWidgetItem(schedule.start_time))
                self.schedules_table.setItem(i, 4, QTableWidgetItem(schedule.end_time))
                
                # Delete button
                delete_btn = QPushButton("Xoá")
                delete_btn.clicked.connect(lambda _, s=schedule.id: self.delete_schedule(s))
                
                self.schedules_table.setCellWidget(i, 5, delete_btn)
        finally:
            session.close()
    
    def delete_schedule(self, schedule_id):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xoá lịch học này?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            session = Session()
            try:
                schedule = session.query(Schedule).filter_by(id=schedule_id).first()
                
                if schedule:
                    # Delete from database
                    session.delete(schedule)
                    session.commit()
                    
                    QMessageBox.information(self, "Thành công", "Đã xoá lịch học")
                    
                    # Reload schedules
                    self.load_schedules()
                    self.load_schedule_combo()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy lịch học")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xoá lịch học: {str(e)}")
            finally:
                session.close()
    
    def load_schedule_combo(self):
        self.schedule_combo.clear()
        
        session = Session()
        try:
            # Get schedules from today onwards
            today = datetime.datetime.now().date()
            schedules = session.query(Schedule).filter(
                Schedule.date >= today
            ).order_by(Schedule.date).all()
            
            for schedule in schedules:
                display_text = f"{schedule.date.strftime('%Y-%m-%d')} - {schedule.class_name} - {schedule.subject}"
                self.schedule_combo.addItem(display_text, schedule.id)
        finally:
            session.close()
    
    def start_attendance(self):
        """Start the attendance process"""
        try:
            # Get the schedule ID (or use a default one if not available)
            schedule_id = 1
            if hasattr(self, 'schedule_id_input') and hasattr(self.schedule_id_input, 'text'):
                schedule_id_text = self.schedule_id_input.text().strip()
                if schedule_id_text:
                    schedule_id = schedule_id_text
            
            # Clear the attendance table first
            self.prepare_attendance_table()
            
            # Call the face recognition module to process video feed
            # Pass the callback function to update attendance in real-time
            success, result = self.face_recognition.process_video_feed(schedule_id, 
                                                                     update_callback=self.update_attendance_entry)
            
            if success:
                # Final update with complete results
                if isinstance(result, list):
                    # Display in the results section
                    self.display_attendance_results(result)
                    
                    # Save to Excel in the output directory
                    excel_file = self.save_attendance_to_excel(result)
                    
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Điểm Danh Thành Công", 
                                          f"Đã điểm danh {len(result)} học sinh.\n"
                                          f"Kết quả đã được hiển thị và lưu tại:\n{excel_file}")
                else:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Điểm Danh Thành Công", result)
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Điểm Danh Thất Bại", result)
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in start_attendance: {e}\n{error_details}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi điểm danh: {str(e)}")

    def prepare_attendance_table(self):
        """Prepare the attendance results table"""
        try:
            # Find the specific table widget for attendance results
            table_widget = None
            if hasattr(self, 'attendance_results_table'):
                table_widget = self.attendance_results_table
            else:
                # Find the table by analyzing the UI layout
                from PyQt5.QtWidgets import QTableWidget
                for widget in self.findChildren(QTableWidget):
                    # Look at the headers to identify the attendance table
                    if widget.columnCount() >= 3:
                        header_texts = []
                        for i in range(widget.columnCount()):
                            header_item = widget.horizontalHeaderItem(i)
                            if header_item:
                                header_texts.append(header_item.text())
                        
                        # Check if this looks like an attendance table
                        if any("Tên" in text for text in header_texts) and any("Mã" in text for text in header_texts):
                            table_widget = widget
                            break
            
            if table_widget is None:
                print("Could not find attendance results table")
                return
            
            # Clear the table
            table_widget.setRowCount(0)
            
            print("Attendance table prepared")
        except Exception as e:
            print(f"Error preparing attendance table: {e}")

    def update_attendance_entry(self, student_data):
        """Update a single attendance entry in real-time"""
        try:
            # Find the attendance table widget using the same logic as prepare_attendance_table
            table_widget = None
            if hasattr(self, 'attendance_results_table'):
                table_widget = self.attendance_results_table
            else:
                # Find the table by analyzing the UI layout
                from PyQt5.QtWidgets import QTableWidget
                for widget in self.findChildren(QTableWidget):
                    # Look at the headers to identify the attendance table
                    if widget.columnCount() >= 3:
                        header_texts = []
                        for i in range(widget.columnCount()):
                            header_item = widget.horizontalHeaderItem(i)
                            if header_item:
                                header_texts.append(header_item.text())
                        
                        if any("Tên" in text for text in header_texts) and any("Mã" in text for text in header_texts):
                            table_widget = widget
                            break
            
            if table_widget is None:
                print("Could not find attendance table for updating")
                return False
            
            # Check if this student is already in the table
            student_code = student_data['student_code']
            name = student_data['name']
            
            # Look for existing entry
            found = False
            for row in range(table_widget.rowCount()):
                if (table_widget.item(row, 1) and 
                    table_widget.item(row, 1).text() == student_code):
                    # Update existing entry
                    found = True
                    break
            
            if not found:
                # Add new entry
                from PyQt5.QtWidgets import QTableWidgetItem
                from PyQt5.QtCore import Qt
                
                row = table_widget.rowCount()
                table_widget.setRowCount(row + 1)
                
                # Map column indices based on header texts
                column_indices = {'name': 0, 'code': 1, 'present': 2}
                
                # Try to find correct columns based on headers
                for i in range(table_widget.columnCount()):
                    header_item = table_widget.horizontalHeaderItem(i)
                    if header_item:
                        header_text = header_item.text().lower()
                        if "tên" in header_text:
                            column_indices['name'] = i
                        elif "mã" in header_text:
                            column_indices['code'] = i
                        elif "có mặt" in header_text or "present" in header_text:
                            column_indices['present'] = i
                
                # Student name
                name_item = QTableWidgetItem(name)
                table_widget.setItem(row, column_indices['name'], name_item)
                
                # Student code
                code_item = QTableWidgetItem(student_code)
                table_widget.setItem(row, column_indices['code'], code_item)
                
                # Status "Có Mặt"
                status_item = QTableWidgetItem("Có")
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setBackground(Qt.green)
                table_widget.setItem(row, column_indices['present'], status_item)
                
                print(f"Added student {name} ({student_code}) to attendance table")
            
            # Make sure the new row is visible
            table_widget.scrollToBottom()
            
            return True
        except Exception as e:
            import traceback
            print(f"Error updating attendance entry: {e}\n{traceback.format_exc()}")
            return False

    def save_attendance_to_excel(self, attendance_data):
        """Save attendance data to an Excel file in the output directory"""
        try:
            if not attendance_data:
                print("No attendance data to export")
                return False
            
            import pandas as pd
            import os
            from datetime import datetime
            
            # Create DataFrame
            df = pd.DataFrame(attendance_data)
            
            # Generate output filename with current date and time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Use output directory in the project folder
            output_dir = "D:\\ProjectTTCS\\output"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f"{output_dir}\\attendance_report_{timestamp}.xlsx"
            
            # Write to Excel with sheet name
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Attendance Report", index=False)
                
                # Access the worksheet to adjust column widths
                worksheet = writer.sheets["Attendance Report"]
                for idx, col in enumerate(df.columns):
                    # Set column width based on maximum length in column plus a buffer
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    # openpyxl column indices are 1-based
                    worksheet.column_dimensions[chr(65 + idx)].width = max_len
            
            print(f"Attendance data saved to {output_file}")
            
            # Show the file in explorer
            import subprocess
            subprocess.Popen(f'explorer /select,"{os.path.abspath(output_file)}"')
            
            return output_file
        except Exception as e:
            import traceback
            print(f"Error saving attendance to Excel: {e}\n{traceback.format_exc()}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lưu Dữ Liệu Thất Bại", 
                              f"Không thể lưu dữ liệu điểm danh: {str(e)}")
            return False

    def display_attendance_results(self, attendance_results):
        """Display final attendance results in the results section"""
        try:
            # Find the attendance results table in the results section
            results_table = None
            
            # Try to find the table widget by name patterns that might indicate results table
            for widget_name in ['results_table', 'attendance_results', 'ket_qua_diem_danh']:
                if hasattr(self, widget_name):
                    results_table = getattr(self, widget_name)
                    break
                    
            # If not found, search all table widgets and try to identify by tab/section name
            if results_table is None:
                from PyQt5.QtWidgets import QTableWidget, QTabWidget
                
                # Look for tabs that might contain "Kết quả" or "Results"
                results_tab = None
                for tab_widget in self.findChildren(QTabWidget):
                    for i in range(tab_widget.count()):
                        tab_text = tab_widget.tabText(i).lower()
                        if "kết quả" in tab_text or "results" in tab_text:
                            results_tab = tab_widget.widget(i)
                            break
                            
                # If we found a results tab, look for tables inside it
                if results_tab:
                    for table in results_tab.findChildren(QTableWidget):
                        results_table = table
                        break
                        
                # If still not found, look for any table in the main window
                if results_table is None:
                    for table in self.findChildren(QTableWidget):
                        results_table = table
                        break
                        
            if results_table is None:
                print("Could not find attendance results table")
                return
                
            # Clear the table
            results_table.setRowCount(0)
            
            # Set the number of rows
            results_table.setRowCount(len(attendance_results))
            
            # Get column indices based on header texts
            column_map = {}
            for i in range(results_table.columnCount()):
                header = results_table.horizontalHeaderItem(i)
                if header:
                    header_text = header.text().lower()
                    if "tên" in header_text:
                        column_map['name'] = i
                    elif "mã" in header_text:
                        column_map['code'] = i
                    elif "có mặt" in header_text or "trạng thái" in header_text:
                        column_map['status'] = i
                        
            # Default indices if headers not found
            if 'name' not in column_map:
                column_map['name'] = 0
            if 'code' not in column_map:
                column_map['code'] = 1
            if 'status' not in column_map:
                column_map['status'] = 2
                
            # Populate table with attendance data
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtCore import Qt
            
            for i, student in enumerate(attendance_results):
                # Student name
                name_item = QTableWidgetItem(student['name'])
                results_table.setItem(i, column_map['name'], name_item)
                
                # Student code
                code_item = QTableWidgetItem(student['student_code'])
                results_table.setItem(i, column_map['code'], code_item)
                
                # Status ("Có mặt")
                status_item = QTableWidgetItem("Có")
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setBackground(Qt.green)
                results_table.setItem(i, column_map['status'], status_item)
                
            print(f"Displayed {len(attendance_results)} students in attendance results table")
        except Exception as e:
            import traceback
            print(f"Error displaying attendance results: {e}\n{traceback.format_exc()}")

    def export_attendance(self):
        if self.schedule_combo.count() == 0:
            QMessageBox.warning(self, "Lỗi", "Không có lịch học nào")
            return
        
        # Get selected schedule ID
        schedule_id = self.schedule_combo.currentData()
        
        if not schedule_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn lịch học")
            return
        
        # Export attendance
        success, result = self.exporter.export_attendance_by_schedule(schedule_id)
        
        if success:
            QMessageBox.information(
                self, "Thành công", 
                f"Đã xuất file điểm danh: {result}"
            )
        else:
            QMessageBox.critical(self, "Lỗi", result)
    
    def export_absent(self):
        # Get date range
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        # Export absent students
        success, result = self.exporter.export_absent_students(start_date, end_date)
        
        if success:
            QMessageBox.information(
                self, "Thành công", 
                f"Đã xuất file danh sách vắng mặt: {result}"
            )
        else:
            QMessageBox.critical(self, "Lỗi", result)
            
    def refresh_students(self):
        """Refresh the students table with data from database"""
        try:
            # Get the students table
            students_table = None
            
            # Try to directly access the students_table if it exists
            if hasattr(self, 'students_table') and hasattr(self.students_table, 'setRowCount'):
                students_table = self.students_table
            
            # If no students_table, look for other possible names
            if students_table is None:
                for widget_name in ['student_table', 'tableStudents', 'tblStudents', 'studentTable']:
                    if hasattr(self, widget_name) and hasattr(getattr(self, widget_name), 'setRowCount'):
                        students_table = getattr(self, widget_name)
                        break
            
            if students_table is None:
                print("Could not find students table widget")
                return
            
            # Clear the table
            students_table.setRowCount(0)
            
            # Get students from database
            students = self.face_recognition.df
            
            if len(students) == 0:
                print("No students in database")
                return
            
            # Set table rows
            students_table.setRowCount(len(students))
            
            # Populate table with student data
            from PyQt5.QtWidgets import QTableWidgetItem
            for i, (_, student) in enumerate(students.iterrows()):
                students_table.setItem(i, 0, QTableWidgetItem(str(student['student_code'])))
                students_table.setItem(i, 1, QTableWidgetItem(student['name']))
                
                # Add timestamp if available
                if 'timestamp' in student and student['timestamp']:
                    students_table.setItem(i, 2, QTableWidgetItem(str(student['timestamp'])))
            
            print(f"Loaded {len(students)} students into table")
        except Exception as e:
            import traceback
            print(f"Error refreshing students: {e}\n{traceback.format_exc()}")

    def train_face_recognition_model(self):
        """Train the face recognition model to improve accuracy"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QProgressDialog
            from PyQt5.QtCore import Qt
            
            # Show a progress dialog
            progress = QProgressDialog("Training face recognition model...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            # Call the training method
            success, message = self.face_recognition.train_model()
            
            progress.setValue(100)
            
            if success:
                QMessageBox.information(self, "Training Complete", message)
            else:
                QMessageBox.critical(self, "Training Error", message)
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error training model: {e}\n{error_details}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error training model: {str(e)}")

    def setup_train_button(self):
        """Set up the train model button"""
        try:
            # Create a train button if it doesn't exist
            from PyQt5.QtWidgets import QPushButton
            
            if not hasattr(self, 'train_button'):
                self.train_button = QPushButton("Train Model")
                self.train_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
                self.train_button.clicked.connect(self.train_face_recognition_model)
                
                # Add it to the layout - you may need to adjust this based on your UI
                if hasattr(self, 'horizontalLayout'):
                    self.horizontalLayout.addWidget(self.train_button)
                elif hasattr(self, 'verticalLayout'):
                    self.verticalLayout.addWidget(self.train_button)
                else:
                    # Try to find any layout
                    for attr_name in dir(self):
                        if 'layout' in attr_name.lower() and hasattr(getattr(self, attr_name), 'addWidget'):
                            layout = getattr(self, attr_name)
                            layout.addWidget(self.train_button)
                            break
        
        except Exception as e:
            print(f"Error setting up train button: {e}")

    def setup_train_button(self):
        """Add a Train and Verify Model button to the student management interface"""
        try:
            from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMessageBox
            from PyQt5.QtCore import Qt
            
            # Create the button if it doesn't exist
            if not hasattr(self, 'train_verify_button'):
                self.train_verify_button = QPushButton("Train and Verify Model")
                self.train_verify_button.setStyleSheet(
                    "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; border-radius: 4px;"
                )
                self.train_verify_button.clicked.connect(self.train_and_verify_model)
                
                # Find where to add the button - look for the students table or a suitable container
                if hasattr(self, 'students_table'):
                    # Try to find the parent layout of the students table
                    parent = self.students_table.parent()
                    if parent:
                        # Look for an existing layout
                        layout = None
                        for child in parent.children():
                            if isinstance(child, QVBoxLayout) or isinstance(child, QHBoxLayout):
                                layout = child
                                break
                        
                        if not layout:
                            # Create a new layout if needed
                            layout = QVBoxLayout(parent)
                        
                        # Add the button to the layout
                        layout.addWidget(self.train_verify_button)
                else:
                    # Try to find a suitable layout anywhere in the UI
                    for attr_name in dir(self):
                        if 'layout' in attr_name.lower() and hasattr(getattr(self, attr_name), 'addWidget'):
                            layout = getattr(self, attr_name)
                            layout.addWidget(self.train_verify_button)
                            break
        except Exception as e:
            print(f"Error setting up train button: {e}")

    def train_and_verify_model(self):
        """Train and verify the face recognition model"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QProgressDialog
            from PyQt5.QtCore import Qt
            
            # Show a progress dialog
            progress = QProgressDialog("Training face recognition model...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Training Model")
            progress.setValue(10)
            
            # Call the training method
            progress.setLabelText("Step 1/2: Training the model...")
            success, message = self.face_recognition.train_model()
            
            if not success:
                progress.cancel()
                QMessageBox.critical(self, "Training Error", message)
                return
            
            progress.setValue(50)
            progress.setLabelText("Step 2/2: Verifying the model...")
            
            # Verify the model has embeddings
            if not hasattr(self.face_recognition, 'embeddings') or not self.face_recognition.embeddings:
                progress.cancel()
                QMessageBox.warning(self, "Verification Failed", 
                                   "No embeddings were created during training. Add more student images.")
                return
            
            # Count embeddings
            embedding_count = len(self.face_recognition.embeddings)
            
            progress.setValue(100)
            
            # Show success message with verification results
            QMessageBox.information(self, "Training Complete", 
                                    f"Model training and verification complete!\n\n"
                                    f"• {embedding_count} students can now be recognized\n"
                                    f"• {message}\n\n"
                                    f"You can now use face recognition for attendance.")
            
            # Refresh the student list
            self.load_students()
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error training and verifying model: {e}\n{error_details}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error training model: {str(e)}")

    def initialize_extra_buttons(self):
        """Initialize extra buttons like the Train and Verify button"""
        self.setup_train_button()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
