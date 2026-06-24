# -*- coding: utf-8 -*-
"""ADM-INS-03 — BR-06: không tạo duplicate cùng Template + Employee active."""
from __future__ import annotations

from datetime import date

from workflow.ADMIN import create_checklist
from workflow.ADMIN.ins_constants import CREATE_EMPLOYEE, CREATE_OFFICER
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

_SUCCESS_FEEDBACK = ("thành công", "thanh cong")
_DUPLICATE_FEEDBACK = ("trùng", "trung", "đã có", "da co", "đã tồn tại", "da ton tai", "ton tai")


def _normalize_cell(text: str) -> str:
    return " ".join(ln.strip() for ln in (text or "").splitlines() if ln.strip())


def _is_active_status(status: str) -> bool:
    s = (status or "").lower()
    inactive = ("hoàn", "hoan", "complete", "hủy", "huy", "cancel", "đã hủy", "da huy")
    if any(x in s for x in inactive):
        return False
    active = ("chờ", "cho", "đang", "dang", "quá", "qua", "pending", "progress", "overdue", "trễ", "tre")
    return any(x in s for x in active)


def _extract_instance_rows(ctx: WorkflowContext) -> list[dict]:
    headers = ui.table_headers(ctx)
    emp_idx = ui.column_index(headers, "Nhân viên", "Nhan vien") or 1
    chk_idx = ui.column_index(headers, "Checklist") or 2
    status_idx = ui.column_index(headers, "Trạng thái", "Trang thai") or 5
    from_idx = ui.column_index(headers, "Từ ngày", "Tu ngay") or 3

    rows: list[dict] = []
    for tr in ui.data_table_rows(ctx):
        cells = tr.locator("td").all()
        max_idx = max(emp_idx, chk_idx, status_idx, from_idx)
        if len(cells) <= max_idx:
            continue
        rows.append(
            {
                "employee": _normalize_cell(cells[emp_idx].inner_text()),
                "checklist": _normalize_cell(cells[chk_idx].inner_text()),
                "status": cells[status_idx].inner_text().strip(),
                "from_date": ui.parse_vn_date(cells[from_idx].inner_text()),
            }
        )
    return rows


def _active_template_for_employee(ctx: WorkflowContext, employee_name: str) -> str | None:
    ui.search_keyword(ctx, employee_name)
    rows = [r for r in _extract_instance_rows(ctx) if employee_name in r["employee"]]
    if not rows:
        return None
    active_rows = [r for r in rows if _is_active_status(r["status"])] or rows
    today = date.today()
    today_rows = [r for r in active_rows if r["from_date"] == today]
    pick_from = today_rows or active_rows
    pick_from.sort(key=lambda r: r["from_date"] or date.min, reverse=True)
    return pick_from[0]["checklist"]


def _collect_feedback(ctx: WorkflowContext) -> dict:
    texts: list[str] = []
    for sel in (
        ".Toastify__toast",
        ".Toastify__toast-body",
        ".ant-message-notice-content",
        ".ant-notification-notice-message",
        ".ant-modal",
    ):
        for node in ctx.page.locator(sel).all():
            try:
                if not node.is_visible():
                    continue
                text = node.inner_text().strip()
                if text:
                    texts.append(text)
            except Exception:
                continue
    combined = " ".join(texts).lower()
    return {
        "successToast": any(p in combined for p in _SUCCESS_FEEDBACK),
        "duplicateMessage": any(p in combined for p in _DUPLICATE_FEEDBACK),
        "summary": " | ".join(texts)[:240],
    }


def _checklist_row_count(ctx: WorkflowContext) -> int:
    return len([r["checklist"] for r in _extract_instance_rows(ctx)])


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)

    template = _active_template_for_employee(ctx, CREATE_EMPLOYEE)
    if not template:
        return ui.fail_with_shot(
            ctx,
            f"Khong tim thay instance active cua [{CREATE_EMPLOYEE}] — can chay ADM-INS-01 truoc",
            "existing_instance",
        )

    rows_before = _checklist_row_count(ctx)
    create_checklist.open_modal(ctx)
    if not create_checklist.fill_form(
        ctx,
        officer_name=CREATE_OFFICER,
        employee_name=CREATE_EMPLOYEE,
        template_name=template,
    ):
        create_checklist.close_modal(ctx)
        return ui.fail_with_shot(
            ctx,
            f"Khong dien form duplicate — template [{template}], NV [{CREATE_EMPLOYEE}]",
            "duplicate_form",
        )

    create_checklist.submit(ctx)
    feedback = _collect_feedback(ctx)
    ui.shot(ctx, "duplicate_attempt")

    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, CREATE_EMPLOYEE)
    rows_after = _checklist_row_count(ctx)
    created_new = rows_after > rows_before

    create_checklist.close_modal(ctx)

    if created_new:
        return ui.fail_with_shot(
            ctx,
            f"BR-06 vo hieu — van tao them instance [{template}] + NV [{CREATE_EMPLOYEE}]",
            "duplicate_attempt",
            rowsBefore=rows_before,
            rowsAfter=rows_after,
            feedback=feedback.get("summary"),
        )

    if feedback["duplicateMessage"]:
        return pass_result(
            f"BR-06 chan duplicate — toast/modal co thong bao Trung/da co [{template}]",
            rowsBefore=rows_before,
            rowsAfter=rows_after,
            feedback=feedback.get("summary"),
        )

    if feedback["successToast"]:
        return ui.fail_with_shot(
            ctx,
            "FE sai toast — hien [Tao thanh cong] du BR-06 chan (0 instance moi, so dong khong doi)",
            "duplicate_toast_bug",
            rowsBefore=rows_before,
            rowsAfter=rows_after,
            feedback=feedback.get("summary"),
        )

    return ui.fail_with_shot(
        ctx,
        "BR-06 chan nhung thieu thong bao Trung/da co tren toast/modal",
        "duplicate_attempt",
        rowsBefore=rows_before,
        rowsAfter=rows_after,
        feedback=feedback.get("summary"),
    )
