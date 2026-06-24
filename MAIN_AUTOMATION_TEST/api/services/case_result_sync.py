# -*- coding: utf-8 -*-
"""Ghi kết quả chạy case (Pass/Fail) + minh chứng vào testcases.json."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from api.services.testcase_store import load_testcases_json, save_testcases

_SCREENSHOT_LABELS = {
    "template_list_before": "Danh sách template (trước)",
    "template_off": "Template Tuyển dụng — Off",
    "template_on": "Template Tuyển dụng — On (khôi phục)",
    "template_active_before_off": "Template Active — trước khi chuyển Off",
    "template_already_off": "Template đã Off — không cần toggle",
    "template_dropdown": "Dropdown Template — Tạo checklist",
    "error": "Lỗi trong quá trình chạy",
    "error_toast": "Toast lỗi hệ thống",
    "calendar_pick_start": "Chọn ngày bắt đầu (01/06)",
    "calendar_open": "Mở lịch chọn khoảng ngày",
    "calendar_range_selected": "Chọn khoảng ngày",
    "calendar_search_result": "Kết quả lọc theo ngày",
    "date_filter_result": "Bảng sau lọc ngày",
    "status_dropdown_open": "Mở dropdown trạng thái / phạm vi",
    "scope_selected": "Đã chọn Thực hiện cho NV",
    "employee_dropdown_open": "Mở dropdown nhân viên",
    "employee_selected": "Đã chọn Quyền Phạm Năng",
    "filter_result": "Kết quả sau lọc nhân viên",
    "employee_column": "Cột Nhân viên — fullName + accountName",
    "case_result": "Kết quả case (fallback)",
    "error_state": "Trạng thái lỗi / chưa đạt",
    "change_officer_result": "Kết quả đổi cán bộ",
    "emp_confirm_result": "EMPLOYEE xác nhận task",
    "off_confirm_result": "OFFICER xác nhận task",
    "date_filter_result_officer": "OFFICER — bảng sau lọc ngày",
    "detail_from_list_officer": "OFFICER mở chi tiết từ danh sách",
    "detail_from_list_employee": "EMPLOYEE mở chi tiết từ danh sách",
    "verify_create_list": "Kiểm tra danh sách sau tạo",
    "after_logout": "Sau đăng xuất",
    "user_menu_open": "Menu user header",
    "emp_confirm_all": "EMPLOYEE xác nhận hết Đúng hạn",
    "detail_progress": "Chi tiết — tiến độ done/total",
    "detail_opened": "Mở chi tiết checklist",
    "emp_confirm_error": "EMPLOYEE — lỗi xác nhận Đúng hạn",
    "template_create_form": "Form tạo template",
    "template_create_result": "Kết quả tạo template",
    "duplicate_toast_bug": "FE sai toast — báo thành công dù BR-06 chặn",
    "verify_template_search": "Kết quả tìm template",
    "template_search_result": "Tìm kiếm template",
    "template_search_leading_space": "Tìm kiếm template — keyword có space đầu",
    "template_active_before_toggle": "Template trước khi toggle Active",
    "template_edit_filled": "Form sửa template đã điền tên mới",
    "template_edit_result": "Kết quả sửa template",
    "officer_list_scope": "OFFICER — danh sách trong phạm vi",
    "search_result_officer": "OFFICER — kết quả tìm kiếm",
    "after_refresh_officer": "OFFICER — sau làm mới danh sách",
    "late_confirm_modal": "OFFICER — modal xác nhận muộn",
    "undo_result": "OFFICER — kết quả hoàn tác",
    "journal_modal": "Modal nhật ký checklist",
    "cancel_modal": "Modal hủy checklist",
    "after_cancel": "Sau xác nhận hủy checklist",
    "cancel_error_toast": "Toast lỗi hủy checklist",
    "cancel_confirm_click": "Bấm xác nhận hủy trên modal",
    "detail_before_back": "Chi tiết trước khi Quay lại",
    "after_quay_lai": "Sau Quay lại danh sách",
}


def _friendly_screenshot_name(filename: str, case_id: str) -> str:
    stem = Path(filename).stem
    prefix = f"{case_id}_"
    if stem.startswith(prefix):
        stem = stem[len(prefix) :]
    return _SCREENSHOT_LABELS.get(stem, stem.replace("_", " "))


def _collect_images(session_dir: Path, case_id: str, session_id: str) -> list[dict]:
    case_dir = session_dir / case_id
    if not case_dir.is_dir():
        return []
    refs: list[dict] = []
    for png in sorted(case_dir.glob("*.png")):
        refs.append(
            {
                "runId": session_id,
                "runType": "case-run",
                "rel": f"{case_id}/{png.name}",
                "name": _friendly_screenshot_name(png.name, case_id),
            }
        )
    return refs


def apply_case_results(session_dir: Path, results: dict[str, dict]) -> dict:
    """Cập nhật result, testDate, evidenceRuns cho từng case đã chạy."""
    data = load_testcases_json()
    if not data:
        return {}

    session_id = session_dir.name
    today = datetime.now().strftime("%Y-%m-%d")
    by_id = {c["id"]: c for c in data.get("cases", [])}

    for case_id, outcome in results.items():
        case = by_id.get(case_id)
        if not case:
            continue

        result = str(outcome.get("result") or "Untested")
        if result not in ("Pass", "Fail"):
            continue

        runs = case.setdefault("evidenceRuns", [])
        run_number = len(runs) + 1
        images = _collect_images(session_dir, case_id, session_id)

        runs.append(
            {
                "runNumber": run_number,
                "runId": session_id,
                "runType": "case-run",
                "testDate": today,
                "result": result,
                "message": str(outcome.get("message") or ""),
                "images": images,
            }
        )

        case["result"] = result
        case["testDate"] = today
        case["evidenceImages"] = images

    return save_testcases(data)
