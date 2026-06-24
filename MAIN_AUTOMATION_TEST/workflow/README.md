# Workflow — automation flows theo test case

Mỗi case có handler Playwright riêng. Dashboard gọi qua `run_test_cases.py` → `workflow/runner.py`.

## Cấu trúc

| Thư mục | Case | File |
|---------|------|------|
| `ADMIN/` | ADM-LST-01…08 | `adm_lst_01.py` … `adm_lst_08.py` |
| `ADMIN/` | ADM-INS-01…03 | `adm_ins_01.py` … `adm_ins_03.py` |
| `ADMIN/` | Modal tạo checklist | `create_checklist.py` (dùng chung INS) |
| `ADMIN/` | ADM-DTL-01…05 | `detail.py` |
| `ADMIN/` | ADM-TPL-01…08, ADM-TPL-04B | `adm_tpl_*.py` (1 file / case) |
| `OFFICER/` | OFF-LST-01…04, OFF-CFM-01…05 | `off_lst_*.py`, `off_cfm_*.py` |
| `EMPLOYEE/` | EMP-LST-01…04 | `list.py` |
| `EMPLOYEE/` | EMP-CFM-01…03 | `confirm.py` |
| `BR/` | BR-TPL-01 | `br_tpl_01.py` |
| `helpers/` | UI primitives | `checklist_ui.py`, `template_ui.py` |

**Quy ước ADMIN (case đã làm):** mỗi file export `run(ctx: WorkflowContext) -> dict`. Logic pass/fail nằm trong file case; `helpers/` chỉ giữ thao tác UI dùng chung (goto, search, đọc bảng, screenshot…).

## Chạy thử

```bash
cd MAIN_AUTOMATION_TEST
python run_test_cases.py --cases ADM-LST-01 --visible
python run_test_cases.py --cases ADM-INS-01,ADM-INS-02,ADM-INS-03 --visible
```

## Thêm workflow ADMIN mới

1. Tạo `workflow/ADMIN/adm_xxx_yy.py` với `def run(ctx) -> dict`
2. Đăng ký trong `workflow/runner.py` → `_REGISTRY` (dạng `workflow.ADMIN.adm_xxx_yy`)
