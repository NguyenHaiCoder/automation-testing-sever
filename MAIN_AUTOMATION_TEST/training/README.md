# Training — Viết Bảng kiểm thử (Checklist Nhân sự)

Thư mục này chứa chuẩn văn phong khi viết **Quy trình** và các cột liên quan trong bảng kiểm thử.

| File | Nội dung |
|------|----------|
| [quy-trinh-test-case.md](./quy-trinh-test-case.md) | Quy tắc chi tiết + mẫu chuẩn + ví dụ Checklist |
| [mau-tham-chieu.md](./mau-tham-chieu.md) | Bộ mẫu gốc (Visitor / FaceID / Lịch họp) để tham khảo cấu trúc |
| [../scripts/generate_testcases_v2.py](../scripts/generate_testcases_v2.py) | Sinh lại `data/testcases.json` từ explore run + BA |

**Agent / Tester:** Trước khi viết hoặc sửa test case, đọc `quy-trinh-test-case.md`. Mọi cột **Quy trình** phải tuân thủ văn phong đó.

**Nguồn testcase v2:** explore `run_23-06-2026_12-53-02` + `docs/checklist-ba.md` — chạy `python scripts/generate_testcases_v2.py` để tái sinh.
