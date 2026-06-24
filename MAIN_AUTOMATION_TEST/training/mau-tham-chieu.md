# Mẫu tham chiếu — Quy trình (văn phong chuẩn H2Q)

Các mẫu dưới đây là **chuẩn vàng** để học cấu trúc câu. Khi viết test case Checklist Nhân sự, giữ nguyên văn phong này và thay tên màn hình/button cho đúng module.

---

## Điều hướng cơ bản

```
1. Truy cập màn hình Home Page
2. Nhấn button [Đăng ký khách]
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Chọn menu [Quản lý tài khoản]
3. Chọn submenu [Quản lý khách]
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Nhấn button [Quản lý lịch họp] ở màn hình Home Page
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Chọn menu [Danh sách lịch họp]
```

---

## Form — Upload QR / CCCD

```
1. Truy cập màn hình [Visitor Account Registration]
2. Chọn tab [Upload QR]
3. Upload ảnh CCCD giả mạo
4. Nhấn button [Đăng ký khách]
```

```
1. Truy cập màn hình [Visitor Account Registration]
2. Chọn tab [Upload QR]
3. Upload ảnh CCCD giả mạo
4. Nhập đầy đủ thông tin đăng ký khách
5. Nhập Ngày sinh là ngày hiện tại
6. Nhập Ngày cấp CCCD là ngày hiện tại
7. Nhấn button [Đăng ký khách]
8. Đến màn hình [Cài đặt FaceID] bấm nút [Quay lại]
```

```
1. Truy cập màn hình [Visitor Account Registration]
2. Chọn tab [Upload QR]
3. Upload ảnh CCCD giả mạo
4. Nhập/chọn [Ngày sinh] là ngày tương lai
5. Nhập/chọn [Ngày cấp CCCD] là ngày tương lai
6. Nhấn button [Đăng ký khách]
```

```
1. Truy cập màn hình [Visitor Account Registration]
2. Chọn tab [Upload QR]
3. Upload ảnh CCCD
4. Điền dữ liệu:
- Số CCCD: 012099123456
- Họ và tên: PHẠM THỊ HỒNG NHUNG
- Địa chỉ thường trú: 45 Nguyễn Trãi, P. Thượng Đình, Q. Thanh Xuân, Hà Nội
5. Nhập/chọn thông tin hợp lệ:
- Ngày sinh: 12/03/2001
- Ngày cấp CCCD: 12/03/2021
- Giới tính: Nữ
- Email: nogminh1435434@gmail.com
- Số điện thoại: 0987654321
6. Nhấn button [Đăng ký khách]
```

---

## FaceID

```
1. Truy cập màn hình [FaceID Setup]
2. Upload một lần 9 ảnh khuôn mặt
```

```
1. Truy cập màn hình [FaceID Setup]
2. Upload lần lượt 5 ảnh khuôn mặt hợp lệ với các góc mặt khác nhau
3. Quan sát bộ đếm số lượng ảnh
4. Nhấn button [Hoàn tất đăng ký]
```

```
1. Truy cập màn hình [FaceID Setup]
2. Upload đủ 5 ảnh FaceID hợp lệ
3. Nhấn button [Hoàn tất đăng ký]
```

---

## Phụ thuộc case + duyệt

```
1. Hoàn tất đăng ký tài khoản khách thành công tại case [VFRS-03]
2. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
3. Chọn menu [Quản lý tài khoản]
4. Chọn submenu [Quản lý khách]
5. Tìm kiếm tài khoản khách vừa đăng ký
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Nhấn button [Quản lý lịch họp] ở màn hình Home Page
3. Nhấn button [Tạo cuộc họp mới]
4. Nhập đầy đủ thông tin cuộc họp hợp lệ
5. Nhấn button [Đăng ký]
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Truy cập màn hình [Quản lý lịch họp]
3. Nhấn button [Tạo cuộc họp mới]
4. Nhập đầy đủ thông tin cuộc họp hợp lệ
5. Nhấn button [Đăng ký]
6. Quay lại màn hình [Quản lý lịch họp] (https://qlrv.democloud.xyz/lich-hop-cua-toi)
```

```
1. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
2. Chọn menu [Danh sách lịch họp]
3. Chọn cuộc họp cần xử lý, chọn "Xem lại chi tiết"
4. Nhấn button [Duyệt]
```
