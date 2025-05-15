# Tính Năng Chống Giả Mạo (Anti-Spoofing) trong Hệ Thống Điểm Danh

Hệ thống điểm danh của chúng ta đã được nâng cấp với các tính năng chống giả mạo để ngăn chặn việc sử dụng ảnh tĩnh hoặc video đã được ghi sẵn nhằm đánh lừa hệ thống.

## Các Tính Năng Chống Giả Mạo Đã Triển Khai

### 1. Phân Tích Độ Sâu và Texture
- Kiểm tra gradient và texture tự nhiên của khuôn mặt
- Phát hiện các khuôn mặt phẳng (như ảnh in hoặc hiển thị trên màn hình)
- Phân tích độ chi tiết và độ sâu của các đường nét trên khuôn mặt

### 2. Phân Tích Ánh Sáng và Phản Chiếu
- Kiểm tra các vùng phản chiếu ánh sáng bất thường (thường thấy khi chụp ảnh từ màn hình)
- Phân tích phân bố ánh sáng tự nhiên trên khuôn mặt
- Phát hiện độ sáng đồng đều bất thường trong ảnh tĩnh

### 3. Kiểm Tra Texture Tự Nhiên
- Phân tích entropy (độ ngẫu nhiên) của texture khuôn mặt
- Khuôn mặt thật có độ biến thiên texture cao hơn ảnh in hoặc ảnh trên màn hình
- Phát hiện texture quá mịn hoặc quá đều (dấu hiệu của ảnh giả)

### 4. So Sánh Nhiều Khung Hình
- Thu thập và so sánh các khung hình liên tiếp của cùng một khuôn mặt
- Phát hiện sự chuyển động tự nhiên hoặc thiếu sự chuyển động (ảnh tĩnh)
- Đảm bảo có sự khác biệt tự nhiên giữa các khung hình (chớp mắt, thay đổi biểu cảm nhỏ)

## Cách Thức Hoạt Động

1. Khi một khuôn mặt được phát hiện, hệ thống sẽ thực hiện kiểm tra độ sâu và texture
2. Sau đó, hệ thống phân tích phản chiếu ánh sáng để tìm dấu hiệu của màn hình hoặc giấy in
3. Hệ thống theo dõi khuôn mặt qua thời gian để phát hiện chuyển động tự nhiên
4. Chỉ khi khuôn mặt vượt qua các kiểm tra trên, hệ thống mới thực hiện nhận diện

## Lưu Ý Khi Sử Dụng

- **Ánh sáng**: Đảm bảo khu vực điểm danh có đủ ánh sáng tự nhiên, tránh ánh sáng quá mạnh hoặc quá yếu
- **Chuyển động**: Khuyến khích người dùng thực hiện các chuyển động nhỏ (như quay đầu nhẹ, chớp mắt) khi điểm danh
- **Khoảng cách**: Đặt camera ở khoảng cách thích hợp (không quá xa hoặc quá gần)
- **Góc độ**: Hướng khuôn mặt thẳng vào camera để có kết quả tốt nhất

## Yêu Cầu Hệ Thống

- Camera có độ phân giải tối thiểu 480p
- Ánh sáng đủ để nhìn rõ khuôn mặt
- Không gian không có phản chiếu ánh sáng mạnh vào khuôn mặt

## Nâng Cao Hiệu Quả

Để cải thiện tính chính xác của hệ thống chống giả mạo:
1. Đảm bảo ánh sáng tốt khi đăng ký khuôn mặt
2. Thu thập nhiều góc độ khác nhau của khuôn mặt khi đăng ký
3. Cập nhật cơ sở dữ liệu khuôn mặt định kỳ
