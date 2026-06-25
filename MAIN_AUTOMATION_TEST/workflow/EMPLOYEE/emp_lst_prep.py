# -*- coding: utf-8 -*-
"""Chuẩn bị EMP-LST — ADMIN template, OFF [Tạo checklist] (ngày hôm nay), EMP chỉ xem/tìm."""
from __future__ import annotations

from pathlib import Path

from workflow.OFFICER import off_lst_prep as off_prep
from workflow.OFFICER.off_constants import ASSIGN_EMPLOYEE, OFFICER_CAN_BO
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui

EMP_LST01_MARKER = "_emp_lst01_checklist.txt"
EMP_CFM02_MARKER = "_emp_cfm02_checklist.txt"
_ROOT = Path(__file__).resolve().parents[2]


def _marker_paths(ctx: WorkflowContext, filename: str) -> list[Path]:
    data_marker = _ROOT / "data" / filename
    session_marker = ctx.run_dir.parent / filename
    return [session_marker, data_marker]


def remember_emp_lst_keyword(ctx: WorkflowContext, keyword: str) -> None:
    text = keyword.strip()
    for marker in _marker_paths(ctx, EMP_LST01_MARKER):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(text, encoding="utf-8")


def resolve_emp_lst_keyword(ctx: WorkflowContext) -> str | None:
    """Ưu tiên marker cùng batch → data/ persistent."""
    for marker in _marker_paths(ctx, EMP_LST01_MARKER):
        if marker.is_file():
            name = marker.read_text(encoding="utf-8").strip()
            if name:
                return name
    return None


def remember_emp_cfm02_checklist(
    ctx: WorkflowContext,
    template_name: str,
    task_number: int | None = None,
) -> None:
    """Lưu checklist EMP-CFM-02 đã [Muộn] — EMP-CFM-03 xem nhật ký cùng instance."""
    lines = [template_name.strip()]
    if task_number is not None:
        lines.append(str(task_number))
    text = "\n".join(lines)
    for marker in _marker_paths(ctx, EMP_CFM02_MARKER):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(text, encoding="utf-8")


def resolve_emp_cfm02_checklist(ctx: WorkflowContext) -> tuple[str | None, int | None]:
    """Đọc checklist + task number từ EMP-CFM-02 (session hoặc data/)."""
    for marker in _marker_paths(ctx, EMP_CFM02_MARKER):
        if not marker.is_file():
            continue
        lines = [ln.strip() for ln in marker.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            continue
        name = lines[0]
        task_num: int | None = None
        if len(lines) > 1:
            try:
                task_num = int(lines[1])
            except ValueError:
                task_num = None
        return name, task_num
    return None, None


def admin_create_template(ctx: WorkflowContext, template_name: str) -> bool:
    """ADMIN tạo template — EMP/OFF không tạo template trong EMP-LST-01."""
    return off_prep.create_template_two_tasks(ctx, template_name, OFFICER_CAN_BO)


def officer_create_checklist_today(ctx: WorkflowContext, template_name: str) -> bool:
    """
    OFFICER đăng nhập → màn [Danh sách checklist] → [Tạo checklist]
    → chọn template, NV [TK Chuyên Viên], StartDate = hôm nay → Lưu.
    EMP không tham gia bước này.
    """
    return off_prep.create_checklist_instance(
        ctx,
        template_name,
        OFFICER_CAN_BO,
        ASSIGN_EMPLOYEE,
    )


def prep_checklist_for_employee_search(ctx: WorkflowContext) -> str | None:
    """
    EMP-LST-02 chạy đơn lẻ: ADMIN template → OFF [Tạo checklist] → logout → EMP login.
    Trả về keyword; None nếu prep thất bại.
    """
    template_name = off_prep.next_assignees_template_name()
    ctx.login_admin()
    if not admin_create_template(ctx, template_name):
        return None
    ui.switch_role_login(ctx, "OFFICER")
    if not officer_create_checklist_today(ctx, template_name):
        return None
    remember_emp_lst_keyword(ctx, template_name)
    logout_and_login_employee(ctx)
    return template_name


def ensure_emp_lst_keyword(ctx: WorkflowContext) -> tuple[str | None, bool]:
    """
    Lấy keyword tìm kiếm cho EMP-LST-02.
    Trả về (keyword, did_prep) — did_prep=True nghĩa là đã login EMPLOYEE sau prep.
    """
    keyword = resolve_emp_lst_keyword(ctx)
    if keyword:
        return keyword, False
    keyword = prep_checklist_for_employee_search(ctx)
    if keyword:
        return keyword, True
    return None, False


def logout_and_login_employee(ctx: WorkflowContext) -> None:
    """Đăng xuất OFF → đăng nhập EMPLOYEE (TK Chuyên Viên)."""
    if not ui.logout_header(ctx):
        ctx.log("Logout OFF that bai — clear cookies", "WARN")
        ctx.page.context.clear_cookies()
        ctx.page.goto(ctx.settings.base_url, wait_until="domcontentloaded", timeout=60000)
        ctx.page.wait_for_timeout(1000)
    ctx.login_as("EMPLOYEE")


def rows_matching_keyword(ctx: WorkflowContext, keyword: str) -> int:
    target = keyword.strip().lower()
    count = 0
    for row in ui.data_table_rows(ctx):
        if target in row.inner_text().lower():
            count += 1
    return count


def open_employee_detail_for_template(ctx: WorkflowContext, template_name: str) -> bool:
    """Danh sách checklist → tìm tên → mở chi tiết (EMPLOYEE)."""
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, template_name)
    target = template_name.strip().lower()
    for row in ui.data_table_rows(ctx):
        if target not in row.inner_text().lower():
            continue
        row.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_employee")
            return True
        link = row.locator("a").first
        if link.count():
            link.click(timeout=8000)
            ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_employee")
            return True
    return False


def prep_officer_checklist_today(ctx: WorkflowContext) -> str | None:
    """ADMIN template → OFF [Tạo checklist] hôm nay cho TK Chuyên Viên."""
    template_name = off_prep.next_assignees_template_name()
    ctx.login_admin()
    if not admin_create_template(ctx, template_name):
        return None
    ui.switch_role_login(ctx, "OFFICER")
    if not officer_create_checklist_today(ctx, template_name):
        return None
    remember_emp_lst_keyword(ctx, template_name)
    return template_name


def prep_officer_overdue_checklist(ctx: WorkflowContext) -> str | None:
    """ADMIN template → OFF [Tạo checklist] quá hạn (StartDate quá khứ) cho TK Chuyên Viên."""
    template_name = off_prep.next_assignees_template_name()
    ctx.login_admin()
    if not admin_create_template(ctx, template_name):
        return None
    ui.switch_role_login(ctx, "OFFICER")
    if not off_prep.create_overdue_checklist_instance(
        ctx, template_name, OFFICER_CAN_BO, ASSIGN_EMPLOYEE
    ):
        return None
    remember_emp_lst_keyword(ctx, template_name)
    return template_name
