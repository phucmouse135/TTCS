# filepath: D:/ProjectTTCS/app/gui.py
from PyQt5.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QTabWidget, QMessageBox, QHeaderView,
                             QLineEdit, QFormLayout, QDateEdit, QTimeEdit, QComboBox, QFileDialog,
                             QDialog, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QPixmap
import os
import pandas as pd
import cv2
import numpy as np
from datetime import datetime

from app.face_recognition import FaceRecognition

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống điểm danh học sinh")
        self.setGeometry(100, 100, 1200, 700)
        
        # Initialize face recognition
        self.face_recognition = FaceRecognition()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup all tabs
        self.setup_student_tab()
        self.setup_schedule_tab()
        self.setup_attendance_tab()
        self.setup_report_tab()
    
    def setup_student_tab(self):
        # Create student tab
        student_tab = QWidget()
        layout = QVBoxLayout(student_tab)
        
        # Add title
        title = QLabel("Quản lý học sinh")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create form layout for adding students
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Student name input
        self.student_name_input = QLineEdit()
        form_layout.addRow("Tên Học Sinh:", self.student_name_input)
        
        # Student ID input
        self.student_id_input = QLineEdit()
        form_layout.addRow("Mã Học Sinh:", self.student_id_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add student button
        add_button = QPushButton("Thêm Học Sinh")
        add_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        add_button.clicked.connect(self.add_student)
        buttons_layout.addWidget(add_button)
        
        # Capture face button
        capture_button = QPushButton("Chụp Ảnh Khuôn Mặt")
        capture_button.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        ''')
        capture_button.clicked.connect(self.capture_student_face)
        buttons_layout.addWidget(capture_button)
        
        # Train model button
        train_button = QPushButton("Train Mô Hình")
        train_button.setStyleSheet('''
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
        ''')
        train_button.clicked.connect(self.train_and_verify_model)
        buttons_layout.addWidget(train_button)
        
        # Add buttons layout to form
        form_layout.addRow("", buttons_layout)
        
        # Add form to main layout
        layout.addWidget(form_widget)
        
        # Create students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(3)
        self.students_table.setHorizontalHeaderLabels(["Tên Học Sinh", "Mã Học Sinh", "Hành Động"])
        self.students_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.students_table)
        
        # Add to tab widget
        self.tab_widget.addTab(student_tab, "Học Sinh")
        
        # Load students
        self.load_students()
    
    def setup_schedule_tab(self):
        # Create schedule tab
        schedule_tab = QWidget()
        layout = QVBoxLayout(schedule_tab)
        
        # Add title
        title = QLabel("Quản lý lịch học")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create form layout for adding schedules
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Class name input
        self.class_name_input = QLineEdit()
        form_layout.addRow("Tên Lớp:", self.class_name_input)
        
        # Subject input
        self.subject_input = QLineEdit()
        form_layout.addRow("Môn Học:", self.subject_input)
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Ngày:", self.date_input)
        
        # Start time input
        self.start_time_input = QTimeEdit()
        self.start_time_input.setTime(QTime(8, 0))
        form_layout.addRow("Giờ Bắt Đầu:", self.start_time_input)
        
        # End time input
        self.end_time_input = QTimeEdit()
        self.end_time_input.setTime(QTime(9, 30))
        form_layout.addRow("Giờ Kết Thúc:", self.end_time_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add schedule button
        add_schedule_button = QPushButton("Thêm Lịch Học")
        add_schedule_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        add_schedule_button.clicked.connect(self.add_schedule)
        buttons_layout.addWidget(add_schedule_button)
        
        # Add buttons layout to form
        form_layout.addRow("", buttons_layout)
        
        # Add form to main layout
        layout.addWidget(form_widget)
        
        # Create schedules table
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels(["Ngày", "Lớp", "Môn Học", "Bắt Đầu", "Kết Thúc", "Hành Động"])
        self.schedules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.schedules_table)
        
        # Add to tab widget
        self.tab_widget.addTab(schedule_tab, "Lịch Học")
        
        # Load schedules
        self.load_schedules()
    
    def setup_attendance_tab(self):
        # Create attendance tab
        attendance_tab = QWidget()
        layout = QVBoxLayout(attendance_tab)
        
        # Add title
        title = QLabel("Điểm Danh Học Sinh")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add schedule selection
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.schedule_selector = QComboBox()
        self.load_schedule_selector()
        form_layout.addRow("Chọn Lịch Học:", self.schedule_selector)
        
        layout.addWidget(form_widget)
        
        # Add start attendance button
        button_layout = QHBoxLayout()
        start_button = QPushButton("Bắt Đầu Điểm Danh")
        start_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                padding: 10px;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        start_button.clicked.connect(self.start_attendance)
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Add results section
        results_label = QLabel("Kết Quả Điểm Danh")
        results_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-top: 20px;")
        layout.addWidget(results_label)
        
        # Create attendance results table
        self.attendance_results_table = QTableWidget()
        self.attendance_results_table.setColumnCount(3)
        self.attendance_results_table.setHorizontalHeaderLabels(["Tên Học Sinh", "Mã Học Sinh", "Trạng Thái"])
        self.attendance_results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.attendance_results_table)
        
        # Add to tab widget
        self.tab_widget.addTab(attendance_tab, "Điểm Danh")
    
    def setup_report_tab(self):
        # Create report tab
        report_tab = QWidget()
        layout = QVBoxLayout(report_tab)
        
        # Add title
        title = QLabel("Báo Cáo Điểm Danh")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add filter controls
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        # Date filter
        self.report_date = QDateEdit()
        self.report_date.setCalendarPopup(True)
        self.report_date.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("Ngày:"))
        filter_layout.addWidget(self.report_date)
        
        # Class filter
        self.report_class = QComboBox()
        self.report_class.addItem("Tất cả các lớp")
        filter_layout.addWidget(QLabel("Lớp:"))
        filter_layout.addWidget(self.report_class)
        
        # Filter button
        filter_button = QPushButton("Lọc")
        filter_button.clicked.connect(self.filter_reports)
        filter_layout.addWidget(filter_button)
        
        # Export button
        export_button = QPushButton("Xuất Báo Cáo")
        export_button.clicked.connect(self.export_report)
        filter_layout.addWidget(export_button)
        
        filter_layout.addStretch()
        
        # Add filters to main layout
        layout.addWidget(filter_widget)
        
        # Create reports table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels(["Ngày", "Lớp", "Môn Học", "Tổng Số", "Có Mặt"])
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.reports_table)
        
        # Add to tab widget
        self.tab_widget.addTab(report_tab, "Báo Cáo")
        
        # Load reports
        self.load_reports()
    
    def load_students(self):
        try:
            # Get students from database
            students = self.face_recognition.df
            
            # Clear table
            self.students_table.setRowCount(0)
            
            if len(students) == 0:
                print("No students in database")
                return
            
            # Add rows to table
            self.students_table.setRowCount(len(students))
            
            # Add students to table
            for i, (_, student) in enumerate(students.iterrows()):
                # Get student info
                name = str(student['name']).strip()
                student_code = str(student['student_code']).strip()
                
                # Create items
                name_item = QTableWidgetItem(name)
                code_item = QTableWidgetItem(student_code)
                
                # Add to table
                self.students_table.setItem(i, 0, name_item)
                self.students_table.setItem(i, 1, code_item)
                
                # Add delete button
                delete_button = QPushButton("Xóa")
                delete_button.setStyleSheet("background-color: #f44336; color: white;")
                delete_button.clicked.connect(lambda checked, code=student_code: self.delete_student_by_id(code))
                self.students_table.setCellWidget(i, 2, delete_button)
            
            print(f"Loaded {len(students)} students into table")
        except Exception as e:
            import traceback
            print(f"Error loading students: {e}\n{traceback.format_exc()}")
    
    def add_student(self):
        try:
            # Get input values
            name = self.student_name_input.text().strip()
            student_code = self.student_id_input.text().strip()
            
            # Validate input
            if not name or not student_code:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin học sinh.")
                return
            
            # Add student to database
            success, message = self.face_recognition.add_student(student_code, name)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                # Clear inputs
                self.student_name_input.clear()
                self.student_id_input.clear()
                # Reload students
                self.load_students()
            else:
                QMessageBox.critical(self, "Lỗi", message)
        except Exception as e:
            import traceback
            print(f"Error adding student: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi thêm học sinh: {str(e)}")
    
    def capture_student_face(self):
        try:
            # Get student code from input
            student_code = self.student_id_input.text().strip()
            
            if not student_code:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã học sinh trước khi chụp ảnh.")
                return
            
            # Check if student exists
            student_exists = False
            for i in range(self.students_table.rowCount()):
                if self.students_table.item(i, 1).text() == student_code:
                    student_exists = True
                    break
            
            if not student_exists:
                QMessageBox.warning(self, "Lỗi", "Học sinh không tồn tại trong hệ thống.")
                return
            
            # Show message
            QMessageBox.information(self, """Chụp Ảnh", 
                                  "Chuẩn bị chụp ảnh khuôn mặt. Hãy đảm bảo khuôn mặt được nhìn rõ."
"
                                  "Nhấn Space để chụp ảnh, ESC để thoát.""")
            
            # Open camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                QMessageBox.critical(self, "Lỗi", "Không thể mở camera.")
                return
            
            # Create directory for student faces if it doesn't exist
            face_dir = os.path.join('data/faces', student_code)
            os.makedirs(face_dir, exist_ok=True)
            
            # Capture face images
            count = 0
            max_images = 5
            
            while count < max_images:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Display frame
                cv2.imshow("Capture Face", frame)
                
                # Check for key press
                key = cv2.waitKey(1)
                
                # ESC to exit
                if key == 27:
                    break
                
                # SPACE to capture
                if key == 32:
                    # Save the image
                    img_path = os.path.join(face_dir, f"{student_code}_{count}.jpg")
                    cv2.imwrite(img_path, frame)
                    count += 1
                    
                    # Show progress
                    print(f"Captured image {count}/{max_images}")
                    
                    # Wait a moment before next capture
                    time.sleep(0.5)
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            
            if count > 0:
                QMessageBox.information(self, "Thành công", 
                                      f"Đã chụp {count} ảnh khuôn mặt cho học sinh có mã {student_code}")
            else:
                QMessageBox.warning(self, "Thông báo", "Không có ảnh nào được chụp.")
        except Exception as e:
            import traceback
            print(f"Error capturing face: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi chụp ảnh: {str(e)}")
    
    def train_and_verify_model(self):
        try:
            # Show progress dialog
            progress = QProgressDialog("Đang huấn luyện mô hình...", "Hủy", 0, 100, self)
            progress.setWindowTitle("Huấn luyện Mô Hình")
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            # Train the model
            progress.setLabelText("Bước 1/2: Đang huấn luyện mô hình...")
            success, message = self.face_recognition.train_model()
            
            if not success:
                progress.cancel()
                QMessageBox.critical(self, "Lỗi Huấn Luyện", message)
                return
            
            progress.setValue(50)
            progress.setLabelText("Bước 2/2: Đang xác minh mô hình...")
            
            # Get number of embeddings
            if hasattr(self.face_recognition, 'embeddings'):
                embedding_count = len(self.face_recognition.embeddings)
            else:
                embedding_count = 0
            
            progress.setValue(100)
            
            # Show success message
            QMessageBox.information(self, "Huấn Luyện Hoàn Tất", 
                                    f"Đã huấn luyện và xác minh mô hình thành công!"
                                    f"• {embedding_count} học sinh có thể được nhận diện"
                                    f"• {message}")
        except Exception as e:
            import traceback
            print(f"Error training model: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi huấn luyện mô hình: {str(e)}")
    
    def delete_student_by_id(self, student_code):
        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa học sinh có mã {student_code}?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Delete student
                success, message = self.face_recognition.delete_student(student_code)
                
                if success:
                    QMessageBox.information(self, "Thành công", message)
                    # Refresh the student list
                    self.load_students()
                else:
                    QMessageBox.critical(self, "Lỗi", message)
        except Exception as e:
            import traceback
            print(f"Error deleting student: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa học sinh: {str(e)}")
    
    def load_schedules(self):
        try:
            # Create schedules database file if it doesn't exist
            schedules_file = 'data/schedules.csv'
            
            if not os.path.exists(schedules_file):
                # Create empty dataframe with columns
                schedules_df = pd.DataFrame(columns=['id', 'date', 'class_name', 'subject', 'start_time', 'end_time'])
                # Save to CSV
                schedules_df.to_csv(schedules_file, index=False)
                print("Created new schedules database")
            
            # Load schedules from CSV
            schedules_df = pd.read_csv(schedules_file)
            
            # Clear table
            self.schedules_table.setRowCount(0)
            
            if len(schedules_df) == 0:
                print("No schedules in database")
                return
            
            # Add rows to table
            self.schedules_table.setRowCount(len(schedules_df))
            
            # Add schedules to table
            for i, (_, schedule) in enumerate(schedules_df.iterrows()):
                # Get schedule info
                schedule_id = str(schedule['id'])
                date = str(schedule['date'])
                class_name = str(schedule['class_name'])
                subject = str(schedule['subject'])
                start_time = str(schedule['start_time'])
                end_time = str(schedule['end_time'])
                
                # Create items
                date_item = QTableWidgetItem(date)
                class_item = QTableWidgetItem(class_name)
                subject_item = QTableWidgetItem(subject)
                start_time_item = QTableWidgetItem(start_time)
                end_time_item = QTableWidgetItem(end_time)
                
                # Add to table
                self.schedules_table.setItem(i, 0, date_item)
                self.schedules_table.setItem(i, 1, class_item)
                self.schedules_table.setItem(i, 2, subject_item)
                self.schedules_table.setItem(i, 3, start_time_item)
                self.schedules_table.setItem(i, 4, end_time_item)
                
                # Add delete button
                delete_button = QPushButton("Xóa")
                delete_button.setStyleSheet("background-color: #f44336; color: white;")
                delete_button.clicked.connect(lambda checked, sid=schedule_id: self.delete_schedule(sid))
                self.schedules_table.setCellWidget(i, 5, delete_button)
            
            print(f"Loaded {len(schedules_df)} schedules into table")
            
            # Also update schedule selector
            self.load_schedule_selector()
        except Exception as e:
            import traceback
            print(f"Error loading schedules: {e}\n{traceback.format_exc()}")
    
    def add_schedule(self):
        try:
            # Get input values
            class_name = self.class_name_input.text().strip()
            subject = self.subject_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            start_time = self.start_time_input.time().toString("hh:mm")
            end_time = self.end_time_input.time().toString("hh:mm")
            
            # Validate input
            if not class_name or not subject:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin lịch học.")
                return
            
            # Load existing schedules
            schedules_file = 'data/schedules.csv'
            
            if os.path.exists(schedules_file):
                schedules_df = pd.read_csv(schedules_file)
            else:
                schedules_df = pd.DataFrame(columns=['id', 'date', 'class_name', 'subject', 'start_time', 'end_time'])
            
            # Generate ID
            if len(schedules_df) == 0:
                new_id = 1
            else:
                new_id = schedules_df['id'].max() + 1
            
            # Add new schedule
            new_schedule = {
                'id': new_id,
                'date': date,
                'class_name': class_name,
                'subject': subject,
                'start_time': start_time,
                'end_time': end_time
            }
            
            schedules_df = pd.concat([schedules_df, pd.DataFrame([new_schedule])], ignore_index=True)
            
            # Save to CSV
            schedules_df.to_csv(schedules_file, index=False)
            
            # Clear inputs
            self.class_name_input.clear()
            self.subject_input.clear()
            
            # Reload schedules
            self.load_schedules()
            
            QMessageBox.information(self, "Thành công", "Đã thêm lịch học mới.")
        except Exception as e:
            import traceback
            print(f"Error adding schedule: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi thêm lịch học: {str(e)}")
    
    def delete_schedule(self, schedule_id):
        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa lịch học này?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Load schedules
                schedules_file = 'data/schedules.csv'
                schedules_df = pd.read_csv(schedules_file)
                
                # Delete schedule
                schedules_df = schedules_df[schedules_df['id'] != int(schedule_id)]
                
                # Save to CSV
                schedules_df.to_csv(schedules_file, index=False)
                
                # Reload schedules
                self.load_schedules()
                
                QMessageBox.information(self, "Thành công", "Đã xóa lịch học.")
        except Exception as e:
            import traceback
            print(f"Error deleting schedule: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa lịch học: {str(e)}")
    
    def load_schedule_selector(self):
        try:
            # Clear selector
            self.schedule_selector.clear()
            
            # Load schedules
            schedules_file = 'data/schedules.csv'
            
            if not os.path.exists(schedules_file):
                return
            
            schedules_df = pd.read_csv(schedules_file)
            
            if len(schedules_df) == 0:
                self.schedule_selector.addItem("Không có lịch học", "-1")
                return
            
            # Add schedules to selector
            for _, schedule in schedules_df.iterrows():
                schedule_id = str(schedule['id'])
                date = str(schedule['date'])
                class_name = str(schedule['class_name'])
                subject = str(schedule['subject'])
                
                # Create schedule text
                schedule_text = f"{date} - {class_name} - {subject}"
                
                # Add to selector
                self.schedule_selector.addItem(schedule_text, schedule_id)
        except Exception as e:
            import traceback
            print(f"Error loading schedule selector: {e}\n{traceback.format_exc()}")
    
    def start_attendance(self):
        try:
            # Get selected schedule
            selected_index = self.schedule_selector.currentIndex()
            
            if selected_index < 0:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn lịch học trước khi điểm danh.")
                return
            
            # Get schedule ID
            schedule_id = self.schedule_selector.itemData(selected_index)
            
            if schedule_id == "-1":
                QMessageBox.warning(self, "Lỗi", "Không có lịch học nào để điểm danh.")
                return
            
            # Initialize attendance data
            self.attendance_data = []
            
            # Clear results table
            self.attendance_results_table.setRowCount(0)
            
            # Start face recognition
            QMessageBox.information(self, "Thông báo", "Bắt đầu điểm danh. Nhấn ESC để dừng.")
            
            # Process video
            success, result = self.face_recognition.process_video_feed(schedule_id)
            
            if success:
                if isinstance(result, list):
                    # Prepare attendance data
                    complete_attendance = self.prepare_attendance_data(result)
                    self.attendance_data = complete_attendance
                    
                    # Display results
                    self.display_attendance_results(complete_attendance)
                    
                    # Save to Excel
                    excel_file = self.save_attendance_to_excel(self.attendance_data)
                    
                    # Save attendance records
                    self.save_attendance_records(schedule_id, result)
                    
                    QMessageBox.information(
                        self, 
                        "Điểm Danh Thành Công", 
                        f"Đã điểm danh {len(result)} học sinh có mặt."
                        f"Kết quả đã được lưu tại:{excel_file}"
                    )
                else:
                    QMessageBox.information(self, "Điểm Danh Thành Công", result)
            else:
                QMessageBox.warning(self, "Điểm Danh Thất Bại", result)
        except Exception as e:
            import traceback
            print(f"Error in start_attendance: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi điểm danh: {str(e)}")
    
    def prepare_attendance_data(self, attendance_results):
        try:
            # Get all students
            all_students = self.face_recognition.get_all_students()
            
            if all_students.empty:
                print("No students in database")
                return []
            
            # Create dictionary of present students
            present_students = {}
            for record in attendance_results:
                student_code = record['student_code']
                present_students[student_code] = record
            
            # Create complete attendance list
            complete_attendance = []
            
            # Add all students
            for _, student in all_students.iterrows():
                student_code = str(student['student_code']).strip()
                name = str(student['name']).strip()
                
                # Check if present
                if student_code in present_students:
                    # Present student
                    complete_attendance.append({
                        'name': name,
                        'student_code': student_code,
                        'status': 'Có mặt',
                        'present': True
                    })
                else:
                    # Absent student
                    complete_attendance.append({
                        'name': name,
                        'student_code': student_code,
                        'status': 'Vắng mặt',
                        'present': False
                    })
            
            print(f"Prepared attendance data for {len(complete_attendance)} students")
            return complete_attendance
        except Exception as e:
            import traceback
            print(f"Error preparing attendance data: {e}\n{traceback.format_exc()}")
            return []
    
    def display_attendance_results(self, attendance_data):
        try:
            # Get the table
            table = self.attendance_results_table
            
            # Clear table
            table.setRowCount(0)
            
            # Set number of rows
            table.setRowCount(len(attendance_data))
            
            # Add data to table
            for i, student in enumerate(attendance_data):
                # Name
                name_item = QTableWidgetItem(student['name'])
                table.setItem(i, 0, name_item)
                
                # ID
                code_item = QTableWidgetItem(student['student_code'])
                table.setItem(i, 1, code_item)
                
                # Status
                status_item = QTableWidgetItem(student['status'])
                status_item.setTextAlignment(Qt.AlignCenter)
                
                # Color based on presence
                if student['present']:
                    status_item.setBackground(Qt.green)
                else:
                    status_item.setBackground(Qt.red)
                    
                table.setItem(i, 2, status_item)
            
            print(f"Displayed {len(attendance_data)} students in attendance results table")
        except Exception as e:
            import traceback
            print(f"Error displaying attendance results: {e}\n{traceback.format_exc()}")
    
    def save_attendance_to_excel(self, attendance_data):
        try:
            if not attendance_data:
                print("No attendance data to export")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(attendance_data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output directory
            output_dir = "D:\ProjectTTCS\output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Full path to Excel file
            output_file = f"{output_dir}\attendance_report_{timestamp}.xlsx"
            
            # Write to Excel
            df.to_excel(output_file, index=False)
            
            print(f"Attendance data saved to {output_file}")
            
            # Open the Excel file
            import subprocess
            subprocess.Popen(f'explorer "{os.path.abspath(output_file)}"')
            
            return output_file
        except Exception as e:
            import traceback
            print(f"Error saving attendance to Excel: {e}\n{traceback.format_exc()}")
            return False
    
    def save_attendance_records(self, schedule_id, attendance_results):
        try:
            # Create attendance records file if it doesn't exist
            records_file = 'data/attendance_records.csv'
            
            if os.path.exists(records_file):
                records_df = pd.read_csv(records_file)
            else:
                records_df = pd.DataFrame(columns=['id', 'schedule_id', 'student_code', 'timestamp'])
            
            # Get schedule info
            schedules_file = 'data/schedules.csv'
            if os.path.exists(schedules_file):
                schedules_df = pd.read_csv(schedules_file)
                schedule_row = schedules_df[schedules_df['id'] == int(schedule_id)]
                
                if len(schedule_row) > 0:
                    class_name = schedule_row.iloc[0]['class_name']
                    subject = schedule_row.iloc[0]['subject']
                    date = schedule_row.iloc[0]['date']
                else:
                    class_name = "Unknown"
                    subject = "Unknown"
                    date = datetime.now().strftime("%Y-%m-%d")
            else:
                class_name = "Unknown"
                subject = "Unknown"
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Generate record ID
            if len(records_df) == 0:
                new_id = 1
            else:
                new_id = records_df['id'].max() + 1
            
            # Create new records
            new_records = []
            for record in attendance_results:
                student_code = record['student_code']
                timestamp = record['timestamp']
                
                new_records.append({
                    'id': new_id,
                    'schedule_id': schedule_id,
                    'student_code': student_code,
                    'timestamp': timestamp,
                    'class_name': class_name,
                    'subject': subject,
                    'date': date
                })
                new_id += 1
            
            # Add to DataFrame
            records_df = pd.concat([records_df, pd.DataFrame(new_records)], ignore_index=True)
            
            # Save to CSV
            records_df.to_csv(records_file, index=False)
            
            print(f"Saved {len(new_records)} attendance records")
            return True
        except Exception as e:
            import traceback
            print(f"Error saving attendance records: {e}\n{traceback.format_exc()}")
            return False
    
    def load_reports(self):
        try:
            # Load attendance records
            records_file = 'data/attendance_records.csv'
            
            if not os.path.exists(records_file):
                print("No attendance records found")
                return
            
            records_df = pd.read_csv(records_file)
            
            if len(records_df) == 0:
                print("No attendance records in database")
                return
            
            # Group by date and class
            if 'date' in records_df.columns and 'class_name' in records_df.columns:
                # Group by date and class
                grouped = records_df.groupby(['date', 'class_name', 'subject'])
                
                # Clear table
                self.reports_table.setRowCount(0)
                
                # Set number of rows
                self.reports_table.setRowCount(len(grouped))
                
                # Add to table
                for i, ((date, class_name, subject), group) in enumerate(grouped):
                    # Count total students for this class
                    total_students = self.count_total_students()
                    
                    # Count present students
                    present_students = len(group['student_code'].unique())
                    
                    # Create items
                    date_item = QTableWidgetItem(date)
                    class_item = QTableWidgetItem(class_name)
                    subject_item = QTableWidgetItem(subject)
                    total_item = QTableWidgetItem(str(total_students))
                    present_item = QTableWidgetItem(str(present_students))
                    
                    # Add to table
                    self.reports_table.setItem(i, 0, date_item)
                    self.reports_table.setItem(i, 1, class_item)
                    self.reports_table.setItem(i, 2, subject_item)
                    self.reports_table.setItem(i, 3, total_item)
                    self.reports_table.setItem(i, 4, present_item)
                
                print(f"Loaded {len(grouped)} reports")
                
                # Also update class filter
                self.update_class_filter()
            else:
                print("Invalid attendance records format")
        except Exception as e:
            import traceback
            print(f"Error loading reports: {e}\n{traceback.format_exc()}")
    
    def count_total_students(self):
        try:
            # Get total students from database
            students = self.face_recognition.df
            return len(students)
        except:
            return 0
    
    def update_class_filter(self):
        try:
            # Clear current items but keep "All classes"
            while self.report_class.count() > 1:
                self.report_class.removeItem(1)
            
            # Load attendance records
            records_file = 'data/attendance_records.csv'
            
            if not os.path.exists(records_file):
                return
            
            records_df = pd.read_csv(records_file)
            
            if 'class_name' in records_df.columns:
                # Get unique class names
                classes = sorted(records_df['class_name'].unique())
                
                # Add to combo box
                for class_name in classes:
                    self.report_class.addItem(class_name)
        except Exception as e:
            print(f"Error updating class filter: {e}")
    
    def filter_reports(self):
        try:
            # Get filter values
            date = self.report_date.date().toString("yyyy-MM-dd")
            class_name = self.report_class.currentText()
            
            # Load attendance records
            records_file = 'data/attendance_records.csv'
            
            if not os.path.exists(records_file):
                print("No attendance records found")
                return
            
            records_df = pd.read_csv(records_file)
            
            if len(records_df) == 0:
                print("No attendance records in database")
                return
            
            # Apply filters
            if class_name != "Tất cả các lớp":
                records_df = records_df[records_df['class_name'] == class_name]
            
            # Filter by date if it's in the dataframe
            if 'date' in records_df.columns:
                records_df = records_df[records_df['date'] == date]
            
            # Group by date and class
            if 'date' in records_df.columns and 'class_name' in records_df.columns:
                # Group by date and class
                grouped = records_df.groupby(['date', 'class_name', 'subject'])
                
                # Clear table
                self.reports_table.setRowCount(0)
                
                # Set number of rows
                self.reports_table.setRowCount(len(grouped))
                
                # Add to table
                for i, ((date, class_name, subject), group) in enumerate(grouped):
                    # Count total students for this class
                    total_students = self.count_total_students()
                    
                    # Count present students
                    present_students = len(group['student_code'].unique())
                    
                    # Create items
                    date_item = QTableWidgetItem(date)
                    class_item = QTableWidgetItem(class_name)
                    subject_item = QTableWidgetItem(subject)
                    total_item = QTableWidgetItem(str(total_students))
                    present_item = QTableWidgetItem(str(present_students))
                    
                    # Add to table
                    self.reports_table.setItem(i, 0, date_item)
                    self.reports_table.setItem(i, 1, class_item)
                    self.reports_table.setItem(i, 2, subject_item)
                    self.reports_table.setItem(i, 3, total_item)
                    self.reports_table.setItem(i, 4, present_item)
                
                print(f"Filtered to {len(grouped)} reports")
            else:
                print("Invalid attendance records format")
        except Exception as e:
            import traceback
            print(f"Error filtering reports: {e}\n{traceback.format_exc()}")
    
    def export_report(self):
        try:
            # Get current reports in table
            rows = self.reports_table.rowCount()
            cols = self.reports_table.columnCount()
            
            if rows == 0:
                QMessageBox.warning(self, "Thông báo", "Không có dữ liệu để xuất.")
                return
            
            # Create data for export
            data = []
            headers = []
            
            # Get headers
            for col in range(cols):
                header_item = self.reports_table.horizontalHeaderItem(col)
                headers.append(header_item.text())
            
            # Get data
            for row in range(rows):
                row_data = {}
                for col in range(cols):
                    item = self.reports_table.item(row, col)
                    if item:
                        row_data[headers[col]] = item.text()
                    else:
                        row_data[headers[col]] = ""
                data.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output directory
            output_dir = "D:\ProjectTTCS\output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Lưu báo cáo", 
                f"{output_dir}\report_{timestamp}.xlsx", 
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # Write to Excel
            df.to_excel(file_path, index=False)
            
            print(f"Report saved to {file_path}")
            
            # Open the Excel file
            import subprocess
            subprocess.Popen(f'explorer "{os.path.abspath(file_path)}"')
            
            QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo tới:{file_path}")
        except Exception as e:
            import traceback
            print(f"Error exporting report: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất báo cáo: {str(e)}")
