# Ứng Dụng Điểm Danh Học Sinh bằng Nhận Diện Khuôn Mặt

Ứng dụng sử dụng công nghệ nhận diện khuôn mặt FaceNet để tự động điểm danh học sinh theo lịch học.

## Tính năng chính

- Quản lý dữ liệu học sinh và lịch học
- Nhận diện khuôn mặt bằng mô hình FaceNet
- Tự động điểm danh theo lịch học
- Xuất báo cáo điểm danh ra file Excel
- Theo dõi danh sách vắng mặt

## Yêu cầu hệ thống

- Python 3.10+
- Camera (webcam)
- Windows, macOS, hoặc Linux

## Cài đặt

1. Clone repository:
```
git clone <repository-url>
cd <repository-folder>
```

2. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Khởi chạy ứng dụng:
```
python main.py
```

## Hướng dẫn sử dụng

### Quản lý học sinh

- Tab "Quản Lý Học Sinh" cho phép thêm, xóa và quản lý thông tin học sinh
- Có thể tải lên ảnh khuôn mặt hoặc chụp ảnh trực tiếp từ camera
- Mã học sinh là duy nhất và được sử dụng để nhận diện

### Quản lý lịch học

- Tab "Quản Lý Lịch Học" cho phép tạo và quản lý các buổi học
- Mỗi lịch học bao gồm ngày, lớp, môn học, giờ bắt đầu và kết thúc

### Điểm danh

- Tab "Điểm Danh" cho phép bắt đầu quá trình điểm danh
- Chọn lịch học và nhấn "Bắt Đầu Điểm Danh"
- Hệ thống sẽ sử dụng camera để nhận diện học sinh
- Sau khi hoàn thành, kết quả sẽ được hiển thị trong bảng
- Có thể xuất kết quả ra file Excel bằng cách nhấn "Xuất File Excel"

### Báo cáo

- Tab "Báo Cáo" cho phép tạo báo cáo điểm danh
- Chọn khoảng thời gian và xuất danh sách vắng mặt

## Quy trình hoạt động

1. Thêm học sinh và ảnh khuôn mặt vào hệ thống
2. Tạo lịch học cho các lớp
3. Khi đến giờ học, chọn lịch học tương ứng và bắt đầu điểm danh
4. Hệ thống sẽ tự động nhận diện học sinh và đánh dấu có mặt/vắng mặt
5. Xuất kết quả điểm danh ra file Excel để lưu trữ

## Cấu trúc dự án

```
ProjectTTCS/
├── app/
│   ├── database.py     # Mô hình cơ sở dữ liệu
│   ├── exporter.py     # Xuất dữ liệu ra Excel
│   ├── face_recognition.py  # Nhận diện khuôn mặt
│   ├── gui.py          # Giao diện người dùng
├── data/
│   ├── embeddings/     # Lưu trữ embedding khuôn mặt
│   ├── student_images/ # Lưu trữ ảnh học sinh
├── models/             # Lưu trữ mô hình học máy
├── output/             # Thư mục xuất file Excel
├── main.py             # Điểm vào chương trình
└── requirements.txt    # Các thư viện cần thiết
```

## Công nghệ sử dụng

- **Python**: Ngôn ngữ lập trình chính
- **FaceNet/MTCNN**: Mô hình nhận diện khuôn mặt
- **PyQt5**: Xây dựng giao diện người dùng
- **SQLAlchemy**: ORM cho cơ sở dữ liệu
- **Pandas/Openpyxl**: Xuất dữ liệu ra Excel
- **OpenCV**: Xử lý hình ảnh và camera
- **SQLite**: Lưu trữ dữ liệu cục bộ
