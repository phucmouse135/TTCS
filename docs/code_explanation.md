# Giải Thích Ý Nghĩa Các Hàm Trong Mã Nguồn Chính

Tài liệu này cung cấp giải thích chi tiết về các hàm quan trọng trong các file mã nguồn chính của dự án.

## 1. `app/gui.py`

-   **`MainWindow.__init__(self)`**:
    -   Khởi tạo cửa sổ chính của ứng dụng PyQt5.
    -   Thiết lập giao diện người dùng và các tab chức năng.
    -   Khởi tạo lớp `EnhancedFaceRecognition` để quản lý nhận diện khuôn mặt và chống giả mạo.

-   **`MainWindow.setup_ui(self)`**:
    -   Tạo và cấu hình các tab giao diện người dùng: "Học Sinh", "Lịch Học", "Điểm Danh", "Báo Cáo".
    -   Thiết lập layout và các widget cho mỗi tab.

-   **`MainWindow.setup_student_tab(self)`**:
    -   Thiết lập tab "Học Sinh" để quản lý thông tin học sinh.
    -   Tạo form nhập liệu để thêm học sinh mới.
    -   Tạo bảng hiển thị danh sách học sinh.
    -   Thêm các nút chức năng: "Thêm Học Sinh", "Chụp Ảnh Khuôn Mặt", "Train Mô Hình".

-   **`MainWindow.setup_schedule_tab(self)`**:
    -   Thiết lập tab "Lịch Học" để quản lý thông tin lịch học.
    -   Tạo form nhập liệu để thêm lịch học mới.
    -   Tạo bảng hiển thị danh sách lịch học.
    -   Thêm nút chức năng "Thêm Lịch Học".

-   **`MainWindow.setup_attendance_tab(self)`**:
    -   Thiết lập tab "Điểm Danh" để thực hiện điểm danh học sinh.
    -   Tạo combobox để chọn lịch học.
    -   Thêm nút chức năng "Bắt Đầu Điểm Danh".
    -   Tạo bảng hiển thị kết quả điểm danh.

-   **`MainWindow.setup_report_tab(self)`**:
    -   Thiết lập tab "Báo Cáo" để xem và xuất báo cáo điểm danh.
    -   Thêm các bộ lọc theo ngày và lớp.
    -   Thêm các nút chức năng "Lọc" và "Xuất Báo Cáo".
    -   Tạo bảng hiển thị báo cáo điểm danh.

-   **`MainWindow.load_students(self)`**:
    -   Tải danh sách học sinh từ cơ sở dữ liệu và hiển thị lên bảng "Học Sinh".

-   **`MainWindow.add_student(self)`**:
    -   Thêm học sinh mới vào cơ sở dữ liệu.
    -   Kiểm tra thông tin nhập liệu.
    -   Cập nhật bảng "Học Sinh".

-   **`MainWindow.capture_student_face(self)`**:
    -   Chụp ảnh khuôn mặt học sinh từ webcam.
    -   Lưu ảnh vào thư mục `data/faces/<student_code>`.

-   **`MainWindow.train_and_verify_model(self)`**:
    -   Huấn luyện mô hình nhận diện khuôn mặt bằng cách sử dụng dữ liệu đã thu thập.
    -   Hiển thị thông báo kết quả huấn luyện.

-   **`MainWindow.delete_student_by_id(self, student_code)`**:
    -   Xóa học sinh khỏi cơ sở dữ liệu theo mã học sinh.
    -   Cập nhật bảng "Học Sinh".

-   **`MainWindow.load_schedules(self)`**:
    -   Tải danh sách lịch học từ cơ sở dữ liệu và hiển thị lên bảng "Lịch Học".

-   **`MainWindow.add_schedule(self)`**:
    -   Thêm lịch học mới vào cơ sở dữ liệu.
    -   Kiểm tra thông tin nhập liệu.
    -   Cập nhật bảng "Lịch Học".

-   **`MainWindow.delete_schedule(self, schedule_id)`**:
    -   Xóa lịch học khỏi cơ sở dữ liệu theo ID.
    -   Cập nhật bảng "Lịch Học".

-   **`MainWindow.load_schedule_selector(self)`**:
    -   Tải danh sách lịch học vào combobox "Chọn Lịch Học" trong tab "Điểm Danh".

-   **`MainWindow.start_attendance(self)`**:
    -   Bắt đầu quá trình điểm danh bằng cách sử dụng webcam.
    -   Nhận diện khuôn mặt học sinh và đánh dấu có mặt.
    -   Hiển thị kết quả điểm danh lên bảng "Kết Quả Điểm Danh".

-   **`MainWindow.prepare_attendance_data(self, attendance_results)`**:
    -   Chuẩn bị dữ liệu điểm danh để hiển thị và lưu trữ.
    -   Kết hợp thông tin từ cơ sở dữ liệu học sinh và kết quả nhận diện.

-   **`MainWindow.display_attendance_results(self, attendance_data)`**:
    -   Hiển thị kết quả điểm danh lên bảng "Kết Quả Điểm Danh".

-   **`MainWindow.save_attendance_to_excel(self, attendance_data)`**:
    -   Xuất kết quả điểm danh ra file Excel.

-   **`MainWindow.save_attendance_records(self, schedule_id, attendance_results)`**:
    -   Lưu thông tin điểm danh vào cơ sở dữ liệu.

-   **`MainWindow.load_reports(self)`**:
    -   Tải dữ liệu báo cáo điểm danh từ cơ sở dữ liệu và hiển thị lên bảng "Báo Cáo".

-   **`MainWindow.filter_reports(self)`**:
    -   Lọc báo cáo điểm danh theo ngày và lớp.

-   **`MainWindow.export_report(self)`**:
    -   Xuất báo cáo điểm danh ra file Excel.

## 2. `app/face_recognition.py`

-   **`FaceRecognition.__init__(self, data_dir='data/faces', database_path='data/face_database.csv')`**:
    -   Khởi tạo lớp `FaceRecognition`.
    -   Khởi tạo các mô hình MTCNN (Multi-task Cascaded Convolutional Networks) và InceptionResnetV1.
    -   Tải cơ sở dữ liệu khuôn mặt từ file CSV.

-   **`FaceRecognition.load_database(self)`**:
    -   Tải thông tin học sinh và embeddings khuôn mặt từ file CSV.
    -   Lưu trữ thông tin vào DataFrame `self.df` và dictionary `self.embeddings`.

-   **`FaceRecognition.extract_face(self, img)`**:
    -   Phát hiện khuôn mặt trong ảnh bằng cách sử dụng MTCNN.
    -   Trả về danh sách các khuôn mặt đã được phát hiện.

-   **`FaceRecognition.get_embedding(self, face_img)`**:
    -   Tính toán embedding (đặc trưng) của khuôn mặt bằng cách sử dụng mô hình InceptionResnetV1.
    -   Trả về embedding của khuôn mặt.

-   **`FaceRecognition.add_student(self, student_code, name, img_path)`**:
    -   Thêm học sinh mới vào cơ sở dữ liệu.
    -   Lưu thông tin học sinh và embedding khuôn mặt vào file CSV.

-   **`FaceRecognition.delete_student(self, student_code)`**:
    -   Xóa học sinh khỏi cơ sở dữ liệu.
    -   Xóa thông tin học sinh và embedding khuôn mặt khỏi file CSV.

-   **`FaceRecognition.recognize_face(self, face_img)`**:
    -   Nhận diện khuôn mặt bằng cách so sánh embedding của khuôn mặt với các embeddings đã lưu trữ.
    -   Trả về thông tin học sinh nếu khuôn mặt được nhận diện, ngược lại trả về `None`.

-   **`FaceRecognition.cosine_similarity(self, a, b)`**:
    -   Tính độ tương đồng cosine giữa hai vectors.

-   **`FaceRecognition.collect_faces_from_camera(self, student_code, name, num_samples=20)`**:
     -   Collect face samples from camera for registration

-   **`FaceRecognition.process_video_feed(self, schedule_id, update_callback=None)`**:
    -   Xử lý video từ webcam để nhận diện khuôn mặt và điểm danh học sinh.
    -   Trả về danh sách các học sinh đã được nhận diện.

-   **`FaceRecognition.train_model(self)`**:
    -   Huấn luyện lại mô hình nhận diện khuôn mặt bằng cách sử dụng dữ liệu đã thu thập.

-   **`FaceRecognition.save_to_csv(self)`**:
    -   Lưu cơ sở dữ liệu vào file CSV.

-   **`FaceRecognition.get_all_students(self)`**:
    -   Lấy tất cả học sinh từ cơ sở dữ liệu.

## 3. `app/enhanced_face_recognition.py`

-   **`EnhancedFaceRecognition.__init__(self, data_dir='data/faces', database_path='data/face_database.csv')`**:
    -   Khởi tạo lớp `EnhancedFaceRecognition` kế thừa từ `FaceRecognition`.
    -   Khởi tạo lớp `AntiSpoofing` để thực hiện các kiểm tra chống giả mạo.

-   **`EnhancedFaceRecognition.process_video_feed(self, schedule_id, update_callback=None)`**:
    -   Xử lý video từ webcam để nhận diện khuôn mặt và điểm danh học sinh, tích hợp các kiểm tra chống giả mạo.
    -   Sử dụng `AntiSpoofing` để kiểm tra xem khuôn mặt có phải là thật hay không.
    -   Chỉ điểm danh nếu khuôn mặt vượt qua các kiểm tra chống giả mạo.

## 4. `app/anti_spoofing.py`

-   **`AntiSpoofing.__init__(self)`**:
    -   Khởi tạo lớp `AntiSpoofing`.
    -   Thiết lập các tham số cho các kiểm tra chống giả mạo.

-   **`AntiSpoofing.check_image_depth(self, face_img)`**:
    -   Phân tích độ sâu của ảnh để phát hiện khuôn mặt phẳng (giả mạo).

-   **`AntiSpoofing.check_abnormal_reflections(self, face_img)`**:
    -   Kiểm tra các phản xạ ánh sáng bất thường để phát hiện màn hình hoặc ảnh in.

-   **`AntiSpoofing.check_texture_naturalness(self, face_img)`**:
    -   Kiểm tra độ tự nhiên của texture để phát hiện khuôn mặt giả mạo.

-   **`AntiSpoofing.compare_frames(self, frame1, frame2)`**:
    -   So sánh hai khung hình liên tiếp để phát hiện ảnh tĩnh hoặc video giả mạo.

-   **`AntiSpoofing.is_live_face(self, face_img, previous_face=None)`**:
    -   Thực hiện kiểm tra toàn diện để xác định xem khuôn mặt có phải là thật hay không.
    -   Kết hợp kết quả từ các kiểm tra độ sâu, phản xạ, texture và so sánh khung hình.

## 5. `app/database.py`

-   **`init_db()`**:
    -   Khởi tạo cơ sở dữ liệu bằng cách tạo các bảng nếu chúng chưa tồn tại.

## 6. `train_and_verify.py`

-   **`train_and_verify()`**:
    -   Huấn luyện mô hình nhận diện khuôn mặt và xác minh khả năng nhận diện bằng webcam.
    -   Sử dụng lớp `FaceRecognition` để huấn luyện và nhận diện khuôn mặt.

## 7. `main.py`

-   **`main()`**:
    -   Khởi chạy ứng dụng PyQt5.
    -   Tạo cửa sổ chính và hiển thị giao diện người dùng.
