# Chuẩn viết cột Quy trình — Bảng kiểm thử

## Mục tiêu

Cột **Quy trình** mô tả **hành động cụ thể của tester trên UI**, theo thứ tự thực hiện. Người đọc (và automation) phải biết rõ: **vào đâu → màn hình nào → bấm gì → nhập gì**.

---

## Nguyên tắc cốt lõi

1. **Đánh số tuần tự** — `1.`, `2.`, `3.` … mỗi bước một hành động.
2. **Một bước = một hành động** — không gộp nhiều thao tác khác loại vào một dòng.
3. **Gọi đúng tên UI** — màn hình, button, tab, menu đặt trong `[...]`.
4. **Động từ chuẩn** — dùng đúng cụm dưới đây, không viết mơ hồ.
5. **Tiền đề rõ ràng** — nếu phụ thuộc case khác, ghi `Hoàn tất … tại case [ID]`.
6. **Dữ liệu nhập** — liệt kê từng field; dùng bullet `-` khi nhiều field trong một bước.

---

## Từ vựng / cụm động từ bắt buộc

| Hành động | Cách viết |
|-----------|-----------|
| Mở màn hình | `Truy cập màn hình [Tên màn hình]` hoặc `Truy cập màn hình Home Page` |
| Đăng nhập | `Đăng nhập hệ thống bằng tài khoản ADMIN` / `OFFICER` / `EMPLOYEE` / `Lãnh Đạo` |
| Menu | `Chọn menu [Tên menu]` |
| Submenu | `Chọn submenu [Tên submenu]` |
| Tab | `Chọn tab [Tên tab]` |
| Button | `Nhấn button [Tên button]` |
| Button ở màn cụ thể | `Nhấn button [Tên] ở màn hình [Tên màn]` |
| Nhập một field | `Nhập/chọn [Tên field] là <giá trị>` |
| Nhập nhiều field | `Điền dữ liệu:` rồi bullet từng dòng |
| Upload | `Upload ảnh CCCD` / `Upload một lần 9 ảnh khuôn mặt` |
| Quay lại | `Đến màn hình [X] bấm nút [Quay lại]` |
| Phụ thuộc case | `Hoàn tất đăng ký … tại case [VFRS-03]` |
| Tìm kiếm / lọc | `Nhập [Keyword] vào ô tìm kiếm` → `Nhấn button [Tìm kiếm]` hoặc `Áp dụng bộ lọc` |
| Chọn dòng / record | `Chọn checklist cần xử lý` / `Chọn cuộc họp cần xử lý` |
| Xem chi tiết | `Chọn "Xem lại chi tiết"` hoặc `Nhấn vào dòng checklist đầu tiên` |

---

## Quy ước đặt tên trong `[...]`

- **Màn hình:** tên hiển thị trên UI hoặc tên nghiệp vụ quen thuộc — ví dụ `[Danh sách checklist]`, `[Chi tiết checklist]`, `[Visitor Account Registration]`.
- **Button:** đúng nhãn trên UI — `[Đăng ký]`, `[Tạo cuộc họp mới]`, `[Duyệt]`, `[Hoàn tất đăng ký]`.
- **Menu / tab:** đúng nhãn menu — `[Quản lý tài khoản]`, `[Upload QR]`.
- **Field:** tên label trên form — `[Ngày sinh]`, `[Ngày cấp CCCD]`.
- Có thể kèm URL ở bước cuối khi cần xác minh route: `(https://qlrv.democloud.xyz/hrm/checklist)`.

---

## Cấu trúc bước điển hình

### Luồng đơn giản (2–3 bước)

```
1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Chọn menu [HRM]
3. Chọn submenu [Checklist]
```

### Luồng có thao tác form

```
1. Truy cập màn hình [Visitor Account Registration]
2. Chọn tab [Upload QR]
3. Upload ảnh CCCD
4. Điền dữ liệu:
- Số CCCD: 012099123456
- Họ và tên: PHẠM THỊ HỒNG NHUNG
5. Nhập/chọn thông tin hợp lệ:
- Ngày sinh: 12/03/2001
- Giới tính: Nữ
6. Nhấn button [Đăng ký khách]
```

### Luồng phụ thuộc case trước

```
1. Hoàn tất đăng ký tài khoản khách thành công tại case [VFRS-03]
2. Đăng nhập hệ thống bằng tài khoản Lãnh Đạo
3. Chọn menu [Quản lý tài khoản]
4. Chọn submenu [Quản lý khách]
5. Tìm kiếm tài khoản khách vừa đăng ký
```

---

## ❌ Tránh viết như sau

| Không chuẩn | Vì sao |
|-------------|--------|
| `Truy cập /hrm/checklist` | Thiếu hành động điều hướng (menu/button/màn hình) |
| `Tại màn danh sách, nhập Keyword` | Không ghi rõ ô/control `[Keyword]` |
| `Áp dụng filter` | Không nói bấm button nào |
| `ADMIN thấy danh sách` | Đó là kết quả mong đợi, không phải quy trình |
| `Kiểm tra cột tiến độ` | Là bước verify — đưa sang **Kết quả mong đợi** |

---

## ✅ Áp dụng cho module Checklist Nhân sự

### Ví dụ 1 — CL-List-01 (trước → sau)

**Trước (không chuẩn):**
```
1. Đăng nhập tài khoản ADMIN
2. Truy cập menu HRM → Checklist (route /hrm/checklist)
```

**Sau (chuẩn):**
```
1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Chọn menu [HRM]
3. Chọn submenu [Checklist]
4. Truy cập màn hình [Danh sách checklist]
```

### Ví dụ 2 — CL-List-06 Filter Keyword

**Sau (chuẩn):**
```
1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Truy cập màn hình [Danh sách checklist]
3. Nhập [Keyword] vào ô tìm kiếm (tên nhân viên hoặc tên template)
4. Nhấn button [Tìm kiếm]
```

### Ví dụ 3 — Mở chi tiết checklist từ danh sách

```
1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Truy cập màn hình [Danh sách checklist]
3. Chọn dòng checklist cần xem
4. Nhấn button [Xem chi tiết]
```

### Ví dụ 4 — Tạo template checklist

```
1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Truy cập màn hình [Danh sách template checklist]
3. Nhấn button [Tạo mới]
4. Nhập đầy đủ thông tin template hợp lệ
5. Nhấn button [Lưu]
```

### Ví dụ 5 — EMPLOYEE xác nhận task

```
1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE
2. Truy cập màn hình [Danh sách checklist]
3. Chọn checklist instance của bản thân
4. Truy cập màn hình [Chi tiết checklist]
5. Chọn task cần xác nhận
6. Nhấn button [Xác nhận hoàn thành]
```

---

## Checklist tự kiểm tra trước khi lưu

- [ ] Mỗi bước bắt đầu bằng số `1.`, `2.` …
- [ ] Có `Truy cập màn hình [...]` hoặc `Chọn menu [...]` trước khi thao tác trên màn
- [ ] Mọi button/tab/menu đều có `[Tên chính xác trên UI]`
- [ ] Bước nhập liệu ghi rõ field và giá trị (hoặc mô tả dữ liệu: hợp lệ / giả mạo / ngày tương lai)
- [ ] Không lẫn kết quả mong đợi vào quy trình
- [ ] Case phụ thuộc case khác có dòng `Hoàn tất … tại case [ID]` ở đầu

---

## Tham chiếu

- Mẫu gốc đa module: [mau-tham-chieu.md](./mau-tham-chieu.md)
- Dữ liệu test case hiện tại: `data/testcases.json`
- Excel nguồn: `2. IT_TestCase-Checklist-Cursor.xlsx` (sheet `TEST_CASE_CURSOR`)
