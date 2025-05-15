# filepath: D:/ProjectTTCS/app/gui.py
from PyQt5.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QTabWidget, QMessageBox, QHeaderView,
                             QLineEdit, QFormLayout, QDateEdit, QTimeEdit, QComboBox, QFileDialog,
                             QDialog, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QPixmap
import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
import cv2
import numpy as np
from datetime import datetime
import sqlite3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.face_recognition import FaceRecognition  # Use the correct module path
from app.database import DatabaseManager as Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống điểm danh học sinh")
        self.setGeometry(100, 100, 1200, 700)
        
        # Initialize face recognition
        self.face_recognition = FaceRecognition()
        
        # Database connection
        # Check if 'db' attribute is missing and add it
        if not hasattr(self, 'db'):
            self.db = Database()  # Make sure to import Database class if needed
        
        # Ensure database tables are created
        self.db.create_tables()
        
        # Setup UI
        self.setup_ui()
        
        # Now that UI is fully set up, refresh class list
        try:
            self.refresh_classes_list()
        except:
            pass  # Ignore errors during initial load
    
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
        self.setup_classes_tab()  # Setup the new tab
        self.setup_class_tab()
    
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
    def setup_classes_tab(self):
        """Set up the class management tab with both class management and student assignment sections"""
        # Create class tab using PyQt5
        classes_tab = QWidget()
        main_layout = QVBoxLayout(classes_tab)
        
        # Add title
        title = QLabel("Quản lý Lớp Học")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create horizontal split layout
        split_layout = QHBoxLayout()
        main_layout.addLayout(split_layout)
        
        # Left frame - Class information
        left_frame = QWidget()
        left_layout = QVBoxLayout(left_frame)
        left_title = QLabel("Thông tin lớp học")
        left_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        left_layout.addWidget(left_title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Class ID (hidden)
        self.class_id_input = QLineEdit()
        self.class_id_input.setVisible(False)
        
        # Class name
        self.class_name_input = QLineEdit()
        form_layout.addRow("Tên lớp:", self.class_name_input)
        
        # Class description
        self.class_desc_input = QLineEdit()
        form_layout.addRow("Mô tả:", self.class_desc_input)
        
        left_layout.addLayout(form_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add class button
        add_button = QPushButton("Thêm Lớp")
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        add_button.clicked.connect(self.add_class)
        buttons_layout.addWidget(add_button)
        
        # Update class button
        update_button = QPushButton("Cập Nhật")
        update_button.setStyleSheet("background-color: #2196F3; color: white;")
        update_button.clicked.connect(self.update_class)
        buttons_layout.addWidget(update_button)
        
        # Delete class button
        delete_button = QPushButton("Xóa Lớp")
        delete_button.setStyleSheet("background-color: #f44336; color: white;")
        delete_button.clicked.connect(self.delete_class)
        buttons_layout.addWidget(delete_button)
        
        # Clear form button
        clear_button = QPushButton("Làm Mới")
        clear_button.clicked.connect(self.clear_class_form)
        buttons_layout.addWidget(clear_button)
        
        left_layout.addLayout(buttons_layout)
        
        # Right frame - Class list
        right_frame = QWidget()
        right_layout = QVBoxLayout(right_frame)
        right_title = QLabel("Danh sách lớp học")
        right_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        right_layout.addWidget(right_title)
        
        # Class table
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(4)
        self.classes_table.setHorizontalHeaderLabels(["ID", "Tên Lớp", "Mô Tả", "Ngày Tạo"])
        self.classes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.classes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.classes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.classes_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.classes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.classes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.classes_table.clicked.connect(self.on_class_select)
        
        right_layout.addWidget(self.classes_table)
        
        # Add frames to split layout
        split_layout.addWidget(left_frame)
        split_layout.addWidget(right_frame)
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(classes_tab, "Quản lý Lớp")
        
        ttk.Label(form_frame, text="Mô tả:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.class_desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Thêm lớp", command=self.add_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cập nhật", command=self.update_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa lớp", command=self.delete_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.clear_class_form).pack(side=tk.LEFT, padx=5)
        
        # Right frame - Class list
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for classes
        columns = ("ID", "Tên lớp", "Mô tả", "Ngày tạo")
        self.classes_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.classes_tree.heading("ID", text="ID")
        self.classes_tree.heading("Tên lớp", text="Tên lớp")
        self.classes_tree.heading("Mô tả", text="Mô tả")
        self.classes_tree.heading("Ngày tạo", text="Ngày tạo")
        
        self.classes_tree.column("ID", width=50)
        self.classes_tree.column("Tên lớp", width=150)
        self.classes_tree.column("Mô tả", width=250)
        self.classes_tree.column("Ngày tạo", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.classes_tree.yview)
        self.classes_tree.configure(yscroll=scrollbar.set)
        
        self.classes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.classes_tree.bind("<<TreeviewSelect>>", self.on_class_select)
        
        # Student assignment section
        assign_frame = ttk.LabelFrame(main_frame, text="Phân công học sinh")
        assign_frame.pack(fill=tk.X, expand=False, padx=10, pady=10)
        
        # Class combobox
        combo_frame = ttk.Frame(assign_frame)
        combo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(combo_frame, text="Chọn lớp:").pack(side=tk.LEFT, padx=5)
        self.selected_class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(combo_frame, textvariable=self.selected_class_var, width=30, state="readonly")
        self.class_combo.pack(side=tk.LEFT, padx=5)
        
        # Don't call load_classes() here - remove that line
        # Instead we'll add a method to be called after UI is fully set up
    
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
            
            # Generate filename with timestamp - fix the path issue by removing any control characters
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output directory
            output_dir = "D:\\ProjectTTCS\\output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Full path to Excel file - ensure no control characters in the path
            output_file = f"{output_dir}\\attendance_report_{timestamp}.xlsx"
            
            # Ensure there are no control characters in the filename
            output_file = ''.join(c for c in output_file if ord(c) >= 32)
            
            print(f"Saving attendance data to {output_file}")
            
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
    
    def load_classes(self):
        """Load classes data into the treeview"""
        # Clear existing items
        self.classes_table.setRowCount(0)
        
        # Make sure we're using the correct database object
        if not hasattr(self, 'db'):
            from app.database import Database
            self.db = Database()
        
        # Get classes from database
        try:
            classes = self.db.get_all_classes()
            
            # Add to table
            self.classes_table.setRowCount(len(classes))
            for i, cls in enumerate(classes):
                self.classes_table.setItem(i, 0, QTableWidgetItem(str(cls[0])))
                self.classes_table.setItem(i, 1, QTableWidgetItem(cls[1]))
                self.classes_table.setItem(i, 2, QTableWidgetItem(cls[2]))
                self.classes_table.setItem(i, 3, QTableWidgetItem(cls[3]))
        except Exception as e:
            # If the classes table doesn't exist, make sure it's created
            print(f"Error loading classes: {str(e)}")
            self.db.create_tables()
            # Try loading again (will be empty but at least won't error)
            try:
                classes = self.db.get_all_classes()
                for cls in classes:
                    self.classes_table.insert("", tk.END, values=cls)
            except:
                pass  # If it still fails, just show an empty list
    
    def on_class_select(self):
        """Handle selection of a class in the table"""
        selected_items = self.classes_table.selectedItems()
        if not selected_items:
            return
            
        # Get selected item data
        class_id = selected_items[0].text()
        name = selected_items[1].text()
        description = selected_items[2].text()
        
        # Update form fields
        self.selected_class_id.setText(class_id)
        self.class_name_var.setText(name)
        self.class_description_var.setText(description)
    
    def reset_class_form(self):
        """Clear the class form fields"""
        self.selected_class_id.setText("")
        self.class_name_var.setText("")
        self.class_description_var.setText("")
        
        # Clear selection in table
        self.classes_table.clearSelection()
    
    def add_class(self):
        """Add a new class"""
        name = self.class_name_var.text().strip()
        description = self.class_description_var.text().strip()
        
        if not name:
            QMessageBox.critical(self, "Lỗi", "Tên lớp không được để trống")
            return
        
        # Add to database
        try:
            self.face_recognition.add_class(name, description)
            QMessageBox.information(self, "Thành công", "Thêm lớp học thành công")
            self.load_classes()
            self.reset_class_form()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm lớp học: {str(e)}")
    
    def update_class(self):
        """Update an existing class"""
        class_id = self.selected_class_id.text()
        if not class_id:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn một lớp học để cập nhật")
            return
        
        name = self.class_name_var.text().strip()
        description = self.class_description_var.text().strip()
        
        if not name:
            QMessageBox.critical(self, "Lỗi", "Tên lớp không được để trống")
            return
        
        # Update in database
        try:
            self.face_recognition.update_class(class_id, name, description)
            QMessageBox.information(self, "Thành công", "Cập nhật lớp học thành công")
            self.load_classes()
            self.reset_class_form()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật lớp học: {str(e)}")
    
    def delete_class(self):
        """Delete a class"""
        class_id = self.selected_class_id.text()
        if not class_id:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn một lớp học để xóa")
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa lớp học này?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        
        # Delete from database
        try:
            self.face_recognition.delete_class(class_id)
            QMessageBox.information(self, "Thành công", "Xóa lớp học thành công")
            self.load_classes()
            self.reset_class_form()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa lớp học: {str(e)}")
    
    def setup_class_tab(self):
        """Set up the class management tab with both class management and student assignment sections"""
        # Create a paned window to divide the tab into sections
        paned_window = ttk.PanedWindow(self.class_tab, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Upper section - Class Management
        upper_frame = ttk.Frame(paned_window)
        paned_window.add(upper_frame, weight=1)
        
        # Class information section - left side
        class_info_frame = ttk.LabelFrame(upper_frame, text="Thông tin lớp học")
        class_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Form for class details
        form_frame = ttk.Frame(class_info_frame)
        form_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Class ID (hidden)
        self.class_id_var = tk.IntVar(value=0)
        
        # Class name field
        ttk.Label(form_frame, text="Tên lớp:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.class_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Class description field
        ttk.Label(form_frame, text="Mô tả:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.class_desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons for class operations
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Thêm lớp", command=self.add_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cập nhật", command=self.update_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa lớp", command=self.delete_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.clear_class_form).pack(side=tk.LEFT, padx=5)
        
        # Class list section - right side
        class_list_frame = ttk.LabelFrame(upper_frame, text="Danh sách lớp học")
        class_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for classes
        columns = ("ID", "Tên lớp", "Mô tả", "Ngày tạo")
        self.classes_tree = ttk.Treeview(class_list_frame, columns=columns, show="headings", height=6)
        
        # Configure columns
        self.classes_tree.heading("ID", text="ID")
        self.classes_tree.heading("Tên lớp", text="Tên lớp")
        self.classes_tree.heading("Mô tả", text="Mô tả")
        self.classes_tree.heading("Ngày tạo", text="Ngày tạo")
        
        self.classes_tree.column("ID", width=50)
        self.classes_tree.column("Tên lớp", width=150)
        self.classes_tree.column("Mô tả", width=250)
        self.classes_tree.column("Ngày tạo", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(class_list_frame, orient="vertical", command=self.classes_tree.yview)
        self.classes_tree.configure(yscroll=scrollbar.set)
        
        self.classes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind select event
        self.classes_tree.bind("<<TreeviewSelect>>", self.on_class_select)
        
        # Lower section - Student Assignment
        lower_frame = ttk.LabelFrame(paned_window, text="Phân công học sinh vào lớp")
        paned_window.add(lower_frame, weight=2)
        
        # Class selector for student assignment
        selector_frame = ttk.Frame(lower_frame)
        selector_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selector_frame, text="Chọn lớp học:").pack(side=tk.LEFT, padx=5)
        self.selected_class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(selector_frame, textvariable=self.selected_class_var, state="readonly", width=30)
        self.class_combo.pack(side=tk.LEFT, padx=5)
        self.class_combo.bind("<<ComboboxSelected>>", self.on_class_combo_select)
        
        # Student assignment section
        students_frame = ttk.Frame(lower_frame)
        students_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Available students - left side
        available_frame = ttk.LabelFrame(students_frame, text="Danh sách học sinh có sẵn")
        available_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Mã SV", "Họ tên", "Lớp")
        self.available_students_tree = ttk.Treeview(available_frame, columns=columns, show="headings", height=10)
        
        for col, width, text in zip(columns, [50, 100, 200, 100], ["ID", "Mã SV", "Họ tên", "Lớp"]):
            self.available_students_tree.heading(col, text=text)
            self.available_students_tree.column(col, width=width)
        
        self.available_students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=self.available_students_tree.yview)
        self.available_students_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Assignment buttons - middle
        buttons_frame = ttk.Frame(students_frame)
        buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text=">>", command=self.assign_student, width=5).pack(pady=5)
        ttk.Button(buttons_frame, text="<<", command=self.unassign_student, width=5).pack(pady=5)
        
        # Assigned students - right side
        assigned_frame = ttk.LabelFrame(students_frame, text="Học sinh trong lớp")
        assigned_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.assigned_students_tree = ttk.Treeview(assigned_frame, columns=columns, show="headings", height=10)
        
        for col, width, text in zip(columns, [50, 100, 200, 100], ["ID", "Mã SV", "Họ tên", "Lớp"]):
            self.assigned_students_tree.heading(col, text=text)
            self.assigned_students_tree.column(col, width=width)
        
        self.assigned_students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(assigned_frame, orient="vertical", command=self.assigned_students_tree.yview)
        self.assigned_students_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Now that all attributes are created, we can load data
        try:
            self.load_classes()
            self.update_class_combo()
        except Exception as e:
            print(f"Error initializing class tab: {str(e)}")
            # Make sure the tables exist
            try:
                self.db.create_tables()
            except:
                pass

    def load_classes(self):
        """Load all classes into the treeview"""
        # Clear existing items
        for item in self.classes_tree.get_children():
            self.classes_tree.delete(item)
        
        try:
            # Get classes from database
            classes = self.db.get_all_classes()
            
            # Add to treeview
            for cls in classes:
                self.classes_tree.insert("", tk.END, values=cls)
        except Exception as e:
            print(f"Error loading classes: {str(e)}")
            # Create table if it doesn't exist
            self.db.create_tables()
    
    def update_class_combo(self):
        """Update the class combobox with current classes"""
        try:
            # Get all classes
            classes = self.db.get_all_classes()
            
            # Format for combobox
            class_options = [f"{cls[0]}: {cls[1]}" for cls in classes]
            
            # Update combobox
            self.class_combo["values"] = class_options
        except Exception as e:
            print(f"Error updating class combobox: {str(e)}")
    
    def on_class_select(self, event):
        """Handle class selection in the treeview"""
        selected = self.classes_tree.selection()
        if not selected:
            return
        
        # Get values
        values = self.classes_tree.item(selected[0])["values"]
        
        # Update form fields
        self.class_id_var.set(values[0])
        self.class_name_var.set(values[1])
        self.class_desc_var.set(values[2])
    
    def add_class(self):
        """Add a new class"""
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        try:
            # Add to database
            self.db.add_class(name, desc)
            
            # Refresh data
            self.load_classes()
            self.update_class_combo()
            self.clear_class_form()
            
            messagebox.showinfo("Thành công", "Đã thêm lớp học mới")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm lớp học: {str(e)}")
    
    def update_class(self):
        """Update an existing class"""
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để cập nhật")
            return
        
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        try:
            # Update in database
            self.db.update_class(class_id, name, desc)
            
            # Refresh data
            self.load_classes()
            self.update_class_combo()
            self.clear_class_form()
            
            messagebox.showinfo("Thành công", "Đã cập nhật lớp học")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật lớp học: {str(e)}")
    
    def delete_class(self):
        """Delete a class"""
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để xóa")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học này?"):
            return
        
        try:
            # Delete from database
            self.db.delete_class(class_id)
            
            # Refresh data
            self.load_classes()
            self.update_class_combo()
            self.clear_class_form()
            
            messagebox.showinfo("Thành công", "Đã xóa lớp học")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa lớp học: {str(e)}")
    
    def clear_class_form(self):
        """Clear the class form fields"""
        self.class_id_var.set(0)
        self.class_name_var.set("")
        self.class_desc_var.set("")
        
        # Clear selection
        for selected_item in self.classes_tree.selection():
            self.classes_tree.selection_remove(selected_item)
    
    def on_class_combo_select(self, event):
        """Handle class selection in combobox for student assignment"""
        selected = self.selected_class_var.get()
        if not selected:
            return
        
        # Extract class ID from "ID: Name" format
        class_id = int(selected.split(":")[0])
        
        # Load students for this class
        self.load_students_for_class(class_id)
    
    def load_students_for_class(self, class_id):
        """Load students for the selected class"""
        # Clear both treeviews
        for item in self.available_students_tree.get_children():
            self.available_students_tree.delete(item)
        
        for item in self.assigned_students_tree.get_children():
            self.assigned_students_tree.delete(item)
        
        try:
            # Get all students
            all_students = self.db.get_all_students()
            
            # Get students in this class
            class_students = self.db.get_students_in_class(class_id)
            
            # IDs of students in the class
            class_student_ids = [student[0] for student in class_students]
            
            # Add students to appropriate treeviews
            for student in all_students:
                if student[0] in class_student_ids:
                    self.assigned_students_tree.insert("", tk.END, values=student)
                else:
                    self.available_students_tree.insert("", tk.END, values=student)
        except Exception as e:
            print(f"Error loading students for class: {str(e)}")
    
    def assign_student(self):
        """Assign selected students to the class"""
        # Get selected class
        selected_class = self.selected_class_var.get()
        if not selected_class:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp học")
            return
        
        # Extract class ID
        class_id = int(selected_class.split(":")[0])
        
        # Get selected students
        selected_students = self.available_students_tree.selection()
        if not selected_students:
            messagebox.showerror("Lỗi", "Vui lòng chọn học sinh để thêm vào lớp")
            return
        
        try:
            # Assign each student
            for student_item in selected_students:
                student_values = self.available_students_tree.item(student_item)["values"]
                student_id = student_values[0]
                
                # Add to database
                self.db.assign_student_to_class(student_id, class_id)
            
            # Reload students
            self.load_students_for_class(class_id)
            
            messagebox.showinfo("Thành công", "Đã phân công học sinh vào lớp")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phân công học sinh: {str(e)}")
    
    def unassign_student(self):
        """Remove selected students from the class"""
        # Get selected class
        selected_class = self.selected_class_var.get()
        if not selected_class:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp học")
            return
        
        # Extract class ID
        class_id = int(selected_class.split(":")[0])
        
        # Get selected students
        selected_students = self.assigned_students_tree.selection()
        if not selected_students:
            messagebox.showerror("Lỗi", "Vui lòng chọn học sinh để xóa khỏi lớp")
            return
        
        # Confirm removal
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa các học sinh này khỏi lớp?"):
            return
        
        try:
            # Remove each student
            for student_item in selected_students:
                student_values = self.assigned_students_tree.item(student_item)["values"]
                student_id = student_values[0]
                
                # Remove from database
                self.db.remove_student_from_class(student_id, class_id)
            
            # Reload students
            self.load_students_for_class(class_id)
            
            messagebox.showinfo("Thành công", "Đã xóa học sinh khỏi lớp")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa học sinh khỏi lớp: {str(e)}")

class StudentManagementApp:
    def __init__(self, root):
        # ...existing code...
        
        # Add class management tab to the notebook
        self.class_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.class_tab, text="Quản lý lớp")
        
        # Setup tabs
        # ...existing code...
        self.setup_class_management_tab()
        
    # ...existing code...
    
    def setup_class_management_tab(self):
        # Create main frame for class management
        main_frame = ttk.Frame(self.class_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split the frame horizontally
        left_frame = ttk.LabelFrame(main_frame, text="Thông tin lớp học")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.LabelFrame(main_frame, text="Danh sách lớp học")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Class information form
        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Class ID (hidden variable)
        self.class_id_var = tk.IntVar()
        
        # Class name field
        ttk.Label(form_frame, text="Tên lớp:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.class_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Class description field
        ttk.Label(form_frame, text="Mô tả:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.class_desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons for class operations
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Thêm lớp", command=self.add_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cập nhật", command=self.update_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa lớp", command=self.delete_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.clear_class_form).pack(side=tk.LEFT, padx=5)
        
        # Right frame - Class list
        # Treeview for classes
        columns = ("ID", "Tên lớp", "Mô tả", "Ngày tạo")
        self.classes_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        
        # Set column headings
        self.classes_tree.heading("ID", text="ID")
        self.classes_tree.heading("Tên lớp", text="Tên lớp")
        self.classes_tree.heading("Mô tả", text="Mô tả")
        self.classes_tree.heading("Ngày tạo", text="Ngày tạo")
        
        # Set column widths
        self.classes_tree.column("ID", width=50)
        self.classes_tree.column("Tên lớp", width=150)
        self.classes_tree.column("Mô tả", width=250)
        self.classes_tree.column("Ngày tạo", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.classes_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.classes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.classes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.classes_tree.bind("<<TreeviewSelect>>", self.on_class_select)
        
        # Load classes data
        self.load_classes_data()
    
    def load_classes_data(self):
        # Clear existing items
        for item in self.classes_tree.get_children():
            self.classes_tree.delete(item)
        
        # Get all classes from database
        classes = self.db.get_all_classes()
        
        # Add classes to treeview
        for cls in classes:
            self.classes_tree.insert("", tk.END, values=cls)
    
    def on_class_select(self, event):
        # Get selected item
        selected = self.classes_tree.selection()
        if not selected:
            return
        
        # Get values of selected item
        values = self.classes_tree.item(selected[0], "values")
        
        # Set form fields
        self.class_id_var.set(values[0])
        self.class_name_var.set(values[1])
        self.class_desc_var.set(values[2])
    
    def add_class(self):
        # Get form values
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        # Validate
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        # Add class to database
        try:
            self.db.add_class(name, desc)
            messagebox.showinfo("Thành công", "Đã thêm lớp học mới")
            self.load_classes_data()
            self.clear_class_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm lớp học: {str(e)}")
    
    def update_class(self):
        # Get class ID
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để cập nhật")
            return
        
        # Get form values
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        # Validate
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        # Update class in database
        try:
            self.db.update_class(class_id, name, desc)
            messagebox.showinfo("Thành công", "Đã cập nhật lớp học")
            self.load_classes_data()
            self.clear_class_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật lớp học: {str(e)}")
    
    def delete_class(self):
        # Get class ID
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để xóa")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học này?"):
            return
        
        # Delete class from database
        try:
            self.db.delete_class(class_id)
            messagebox.showinfo("Thành công", "Đã xóa lớp học")
            self.load_classes_data()
            self.clear_class_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa lớp học: {str(e)}")
    
    def clear_class_form(self):
        # Clear form fields
        self.class_id_var.set(0)
        self.class_name_var.set("")
        self.class_desc_var.set("")
        
        # Deselect treeview items
        for selected_item in self.classes_tree.selection():
            self.classes_tree.selection_remove(selected_item)
    
    # ...existing code...
    
    def refresh_classes_list(self):
        """Safely refresh the classes list"""
        try:
            if hasattr(self, 'classes_tree'):
                # Clear existing items
                for item in self.classes_tree.get_children():
                    self.classes_tree.delete(item)
                
                # Get classes from database
                classes = self.db.get_all_classes()
                
                # Add classes to treeview
                for cls in classes:
                    self.classes_tree.insert("", tk.END, values=cls)
                
                # Update class combobox if it exists
                if hasattr(self, 'class_combo'):
                    class_options = [f"{cls[0]}: {cls[1]}" for cls in classes]
                    self.class_combo["values"] = class_options
        except Exception as e:
            print(f"Error refreshing classes list: {str(e)}")

    def on_class_select(self, event):
        """Handle class selection in treeview"""
        selected = self.classes_tree.selection()
        if not selected:
            return
        
        # Get item data
        item = self.classes_tree.item(selected[0])
        values = item["values"]
        
        # Update form fields
        self.class_id_var.set(values[0])
        self.class_name_var.set(values[1])
        self.class_desc_var.set(values[2])

    def add_class(self):
        """Add a new class"""
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        try:
            # Add class to database
            self.db.add_class(name, desc)
            
            # Show success message
            messagebox.showinfo("Thành công", "Đã thêm lớp học mới")
            
            # Clear form
            self.clear_class_form()
            
            # Refresh class list
            self.refresh_classes_list()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm lớp học: {str(e)}")

    def update_class(self):
        """Update an existing class"""
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để cập nhật")
            return
        
        name = self.class_name_var.get().strip()
        desc = self.class_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Lỗi", "Tên lớp không được để trống")
            return
        
        try:
            # Update class in database
            self.db.update_class(class_id, name, desc)
            
            # Show success message
            messagebox.showinfo("Thành công", "Đã cập nhật lớp học")
            
            # Clear form
            self.clear_class_form()
            
            # Refresh class list
            self.refresh_classes_list()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật lớp học: {str(e)}")

    def delete_class(self):
        """Delete a class"""
        class_id = self.class_id_var.get()
        if class_id == 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn một lớp để xóa")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học này?"):
            return
        
        try:
            # Delete class from database
            self.db.delete_class(class_id)
            
            # Show success message
            messagebox.showinfo("Thành công", "Đã xóa lớp học")
            
            # Clear form
            self.clear_class_form()
            
            # Refresh class list
            self.refresh_classes_list()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa lớp học: {str(e)}")

    def clear_class_form(self):
        """Clear the class form fields"""
        self.class_id_var.set(0)
        self.class_name_var.set("")
        self.class_desc_var.set("")
