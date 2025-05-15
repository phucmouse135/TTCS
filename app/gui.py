import sys
import os
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
import cv2
import openpyxl
from openpyxl import Workbook
import subprocess  # For running train_and_verify.py

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.resize(1200, 800)
        self.setWindowTitle("Student Management System")

        self.tab_widget = QTabWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        # Initialize tabs
        self.student_tab = QWidget()
        self.class_tab = QWidget()
        self.schedule_tab = QWidget()
        self.attendance_tab = QWidget()
        self.report_tab = QWidget()

        self.tab_widget.addTab(self.student_tab, "Học Sinh")
        self.tab_widget.addTab(self.class_tab, "Lớp Học")
        self.tab_widget.addTab(self.schedule_tab, "Lịch Học")
        self.tab_widget.addTab(self.attendance_tab, "Điểm Danh")
        self.tab_widget.addTab(self.report_tab, "Báo Cáo")

        # Setup individual tabs
        self.setup_student_tab()
        self.setup_class_tab()
        self.setup_schedule_tab()
        self.setup_attendance_tab()
        self.setup_report_tab()

    def setup_student_tab(self):
        student_layout = QVBoxLayout()

        # Add Student Section
        add_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.id_input = QLineEdit()
        self.image_button = QPushButton("Thêm Ảnh")
        self.train_button = QPushButton("Train Model")

        add_layout.addWidget(QLabel("Tên:"))
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(QLabel("Mã Sinh Viên:"))
        add_layout.addWidget(self.id_input)
        add_layout.addWidget(self.image_button)
        add_layout.addWidget(self.train_button)

        self.image_button.clicked.connect(self.add_student_images)
        self.train_button.clicked.connect(self.train_model)

        student_layout.addLayout(add_layout)

        # Edit/Delete Student Section
        edit_layout = QHBoxLayout()
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(2)
        self.student_table.setHorizontalHeaderLabels(["Tên", "Mã Sinh Viên"])
        edit_layout.addWidget(self.student_table)

        button_layout = QVBoxLayout()
        self.edit_button = QPushButton("Sửa Thông Tin")
        self.delete_button = QPushButton("Xóa Sinh Viên")
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        edit_layout.addLayout(button_layout)

        student_layout.addLayout(edit_layout)

        self.student_tab.setLayout(student_layout)

    def setup_class_tab(self):
        class_layout = QVBoxLayout()

        # Add Class Section
        add_layout = QHBoxLayout()
        self.class_name_input = QLineEdit()
        add_layout.addWidget(QLabel("Tên Lớp:"))
        add_layout.addWidget(self.class_name_input)

        self.add_class_button = QPushButton("Thêm Lớp")
        add_layout.addWidget(self.add_class_button)

        class_layout.addLayout(add_layout)

        # Class Table Section
        self.class_table = QTableWidget()
        self.class_table.setColumnCount(2)
        self.class_table.setHorizontalHeaderLabels(["Tên Lớp", "Số Lượng Sinh Viên"])
        class_layout.addWidget(self.class_table)

        # Assign Students Section
        assign_layout = QHBoxLayout()
        self.student_combo = QComboBox()
        self.class_combo = QComboBox()
        self.assign_button = QPushButton("Phân Công Sinh Viên")

        assign_layout.addWidget(QLabel("Sinh Viên:"))
        assign_layout.addWidget(self.student_combo)
        assign_layout.addWidget(QLabel("Lớp Học:"))
        assign_layout.addWidget(self.class_combo)
        assign_layout.addWidget(self.assign_button)

        class_layout.addLayout(assign_layout)

        self.class_tab.setLayout(class_layout)

    def setup_schedule_tab(self):
        schedule_layout = QVBoxLayout()

        # Add Schedule Section
        add_layout = QHBoxLayout()
        self.schedule_name_input = QLineEdit()
        add_layout.addWidget(QLabel("Tên Lịch Học:"))
        add_layout.addWidget(self.schedule_name_input)

        self.add_schedule_button = QPushButton("Thêm Lịch Học")
        add_layout.addWidget(self.add_schedule_button)

        schedule_layout.addLayout(add_layout)

        # Schedule Table Section
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(1)
        self.schedule_table.setHorizontalHeaderLabels(["Tên Lịch Học"])
        schedule_layout.addWidget(self.schedule_table)

        self.schedule_tab.setLayout(schedule_layout)

    def setup_attendance_tab(self):
        attendance_layout = QVBoxLayout()

        # Start Attendance Section
        self.start_attendance_button = QPushButton("Bắt Đầu Điểm Danh")
        attendance_layout.addWidget(self.start_attendance_button)

        # Attendance Display Section
        self.attendance_display = QTableWidget()
        self.attendance_display.setColumnCount(2)
        self.attendance_display.setHorizontalHeaderLabels(["Tên", "Thời Gian"])
        attendance_layout.addWidget(self.attendance_display)

        self.attendance_tab.setLayout(attendance_layout)

    def setup_report_tab(self):
        report_layout = QVBoxLayout()

        # Generate Report Section
        self.generate_report_button = QPushButton("Xuất Báo Cáo Tổng Hợp")
        report_layout.addWidget(self.generate_report_button)

        self.report_tab.setLayout(report_layout)

    def add_student_images(self):
        # Open file dialog to select 20 images
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_names, _ = QFileDialog.getOpenFileNames(self, "Chọn 20 Ảnh", "", "Images (*.png *.jpg *.jpeg)", options=options)

        if len(file_names) != 20:
            QMessageBox.warning(self, "Cảnh Báo", "Vui lòng chọn đúng 20 ảnh.")
            return

        # TODO: Store the image paths or the images themselves
        QMessageBox.information(self, "Thông Báo", f"Đã chọn {len(file_names)} ảnh.")

    def train_model(self):
        try:
            # Run train_and_verify.py as a separate process
            subprocess.run(["python", "train_and_verify.py"], check=True)
            QMessageBox.information(self, "Thông Báo", "Đã train model thành công.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi train model: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())