# BR-TPL-01 — Template OFF ẩn khỏi dropdown Tạo checklist

Template mục tiêu: **Tuyển dụng** (mã `tuyendung`).

## Mục tiêu

Khi template **Tuyển dụng** bị tắt (Active → **Off**), màn **Checklist nhân sự** → modal **Tạo checklist** → dropdown **Template** **không** hiển thị "Tuyển dụng" → **Pass**.

## Quy trình (test case)

1. Đăng nhập hệ thống bằng tài khoản ADMIN
2. Truy cập màn hình [Mẫu checklist]
3. Tìm dòng template [Tuyển dụng]
4. Nhấn toggle [Trạng thái] để chuyển sang **Off**
5. Truy cập màn hình [Danh sách checklist]
6. Nhấn button [Tạo checklist]
7. Nhấn dropdown [Template]
8. Quan sát danh sách lựa chọn

## Kết quả mong đợi

1. Dropdown Template **không** chứa "Tuyển dụng"
2. Các template Active khác vẫn hiển thị bình thường

## Teardown

- Khôi phục template **Tuyển dụng** về **Active** (nếu trước đó đang Active) để không ảnh hưởng test khác.

## Chạy thử

```bash
cd MAIN_AUTOMATION_TEST
python run_test_cases.py --cases BR-TPL-01 --visible
```

Implementation: `br_tpl_01.py`
