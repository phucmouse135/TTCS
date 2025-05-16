# Hệ Thống Nhận Diện Khuôn Mặt và Điểm Danh Thông Minh

Dự án này phát triển một hệ thống nhận diện khuôn mặt và điểm danh học sinh tự động, sử dụng các kỹ thuật học sâu và các biện pháp chống giả mạo (anti-spoofing) để đảm bảo tính chính xác và an toàn.

## Cấu Trúc Thư Mục

```
ProjectTTCS/
│
├── data/                           # Thư mục chứa dữ liệu
│   ├── faces/                      # Thư mục chứa hình ảnh khuôn mặt của học sinh
│   ├── face_database.csv           # CSV chứa thông tin học sinh và embeddings
│   ├── schedules.csv               # CSV chứa thông tin lịch học
│   └── attendance_records.csv      # CSV chứa thông tin điểm danh
│
├── docs/                           # Tài liệu bổ sung
│   └── anti_spoofing_guide.md      # Hướng dẫn về tính năng chống giả mạo
│
├── app/                            # Mã nguồn chính của ứng dụng
│   ├── __init__.py                 # Khởi tạo gói ứng dụng
│   ├── anti_spoofing.py            # Mã nguồn cho tính năng chống giả mạo
│   ├── database.py                 # Định nghĩa cơ sở dữ liệu (SQLAlchemy)
│   ├── enhanced_face_recognition.py# Lớp nhận diện khuôn mặt nâng cao với chống giả mạo
│   ├── face_recognition.py         # Mã nguồn cho nhận diện khuôn mặt
│   ├── gui.py                      # Giao diện người dùng (PyQt5)
│   ├── exporter.py                 # Xuất báo cáo điểm danh
│
├── train_and_verify.py             # Script huấn luyện và xác minh mô hình
├── main.py                         # Script chính để chạy ứng dụng PyQt5
├── init_db.py                      # Script khởi tạo cơ sở dữ liệu
├── run_app.bat                     # Batch file để chạy ứng dụng
├── requirements.txt                # Các thư viện cần thiết
└── README.md                       # Tài liệu dự án
```

## Ý Nghĩa Của Các File Chính

- **main.py**: Khởi chạy ứng dụng giao diện người dùng PyQt5.
- **app/gui.py**: Định nghĩa giao diện người dùng chính, bao gồm các tab quản lý học sinh, lịch học, điểm danh và báo cáo.
- **app/face_recognition.py**: Chứa lớp `FaceRecognition` để phát hiện, nhận diện khuôn mặt và quản lý cơ sở dữ liệu khuôn mặt.
- **app/enhanced_face_recognition.py**: Chứa lớp `EnhancedFaceRecognition` kế thừa từ `FaceRecognition`, tích hợp thêm các tính năng chống giả mạo.
- **app/anti_spoofing.py**: Chứa lớp `AntiSpoofing` để phát hiện khuôn mặt giả mạo.
- **app/database.py**: Định nghĩa cơ sở dữ liệu sử dụng SQLAlchemy, bao gồm các bảng `Student`, `Schedule`, và `Attendance`.
- **app/exporter.py**: Chứa lớp `AttendanceExporter` để xuất báo cáo điểm danh ra file Excel.
- **train_and_verify.py**: Script để huấn luyện mô hình nhận diện khuôn mặt và kiểm tra khả năng nhận diện.
- **init_db.py**: Script để khởi tạo cơ sở dữ liệu.
- **run_app.bat**: Batch file để chạy ứng dụng trong môi trường ảo.

## Quy Trình Thu Thập Dữ Liệu Khuôn Mặt

1.  **Chuẩn bị**:
    -   Sử dụng webcam để chụp ảnh khuôn mặt học sinh.
    -   Ảnh được lưu trữ trong thư mục `data/faces/<student_code>`.
2.  **Thu thập**:
    -   Giao diện cho phép chụp nhiều ảnh khuôn mặt từ các góc độ khác nhau.
    -   Số lượng ảnh tối thiểu để đảm bảo chất lượng nhận diện.
3.  **Lưu trữ**:
    -   Đường dẫn đến thư mục ảnh được lưu trong file `data/face_database.csv`.
    -   Embeddings (đặc trưng) của khuôn mặt được tính toán và lưu cùng thông tin học sinh.

## Quy Trình Huấn Luyện Mô Hình

1.  **Chuẩn bị dữ liệu**:
    -   Đọc dữ liệu từ `data/face_database.csv`.
    -   Sử dụng các embeddings đã lưu để huấn luyện mô hình.
2.  **Huấn luyện**:
    -   Sử dụng lớp `FaceRecognition` để huấn luyện mô hình.
    -   Mô hình được huấn luyện để phân biệt các khuôn mặt khác nhau.
3.  **Xác minh**:
    -   Sử dụng webcam để kiểm tra khả năng nhận diện khuôn mặt của mô hình.
    -   Hiển thị kết quả nhận diện trên giao diện.

## Hướng Dẫn Sử Dụng Ứng Dụng

### Yêu Cầu Hệ Thống

-   Python 3.7+
-   Webcam
-   Các thư viện được liệt kê trong `requirements.txt`

### Cài Đặt

1.  Clone repository:

    ```
    git clone <repository-url>
    cd ProjectTTCS
    ```
2.  Tạo môi trường ảo (virtual environment):

    ```
    python -m venv venv
    ```
3.  Kích hoạt môi trường ảo:

    -   Trên Windows:

        ```
        venv\Scripts\activate
        ```
    -   Trên Linux/macOS:

        ```
        source venv/bin/activate
        ```
4.  Cài đặt các thư viện cần thiết:

    ```
    pip install -r requirements.txt
    ```

### Cấu Hình

1.  **Cơ sở dữ liệu**:
    -   Ứng dụng sử dụng cơ sở dữ liệu SQLite.
    -   File cơ sở dữ liệu `attendance.db` được tạo trong thư mục `data`.
2.  **File CSV**:
    -   `data/face_database.csv`: Chứa thông tin học sinh và embeddings khuôn mặt.
    -   `data/schedules.csv`: Chứa thông tin lịch học.
    -   `data/attendance_records.csv`: Chứa thông tin điểm danh.

### Chạy Ứng Dụng

1.  **Khởi tạo cơ sở dữ liệu**:

    ```
    python init_db.py
    ```
2.  **Chạy ứng dụng**:

    ```
    python main.py
    ```

    Hoặc sử dụng file `run_app.bat` trên Windows.

## Các Tính Năng Chính

-   **Quản lý học sinh**: Thêm, xóa, sửa thông tin học sinh và chụp ảnh khuôn mặt.
-   **Quản lý lịch học**: Thêm, xóa, sửa thông tin lịch học.
-   **Điểm danh**: Sử dụng webcam để nhận diện khuôn mặt và điểm danh học sinh.
-   **Chống giả mạo (Anti-Spoofing)**: Phát hiện và ngăn chặn việc sử dụng ảnh hoặc video giả mạo để điểm danh.
-   **Báo cáo**: Tạo báo cáo điểm danh theo ngày, lớp, môn học và xuất ra file Excel.

## Tính Năng Chống Giả Mạo (Anti-Spoofing)

Hệ thống tích hợp các kỹ thuật chống giả mạo để ngăn chặn việc sử dụng ảnh hoặc video để gian lận điểm danh:

1.  **Phân tích độ sâu và texture**:
    -   Kiểm tra gradient và texture tự nhiên của khuôn mặt.
    -   Phát hiện các khuôn mặt phẳng (như ảnh in hoặc hiển thị trên màn hình).
2.  **Phân tích ánh sáng và phản chiếu**:
    -   Kiểm tra các vùng phản chiếu ánh sáng bất thường.
    -   Phân tích phân bố ánh sáng tự nhiên trên khuôn mặt.
3.  **Kiểm tra texture tự nhiên**:
    -   Phân tích entropy (độ ngẫu nhiên) của texture khuôn mặt.
    -   Khuôn mặt thật có độ biến thiên texture cao hơn ảnh in hoặc ảnh trên màn hình.
4.  **So sánh nhiều khung hình**:
    -   Thu thập và so sánh các khung hình liên tiếp của cùng một khuôn mặt.
    -   Phát hiện sự chuyển động tự nhiên hoặc thiếu sự chuyển động (ảnh tĩnh).

## Kết Quả và Hiệu Suất

-   Độ chính xác nhận diện khuôn mặt: \~90% (trong điều kiện ánh sáng tốt và khuôn mặt rõ ràng).
-   Thời gian nhận diện: \~0.1 giây/khuôn mặt.
-   Tính năng chống giả mạo giúp giảm thiểu gian lận điểm danh.

## Hướng Phát Triển Tương Lai

-   Cải thiện độ chính xác và tốc độ nhận diện.
-   Tối ưu hóa tính năng chống giả mạo.
-   Phát triển giao diện web để quản lý và báo cáo từ xa.
-   Tích hợp với các hệ thống quản lý học sinh khác.

## Tác Giả

-   Nguyễn Đình Phúc
-   Liên hệ: phucchuot37@gmail.com