# -*- coding: utf-8 -*-
"""ADM-DTL-05 — Hiển thị position và department trên chi tiết (BR-13)."""
from __future__ import annotations

import re

from workflow.ADMIN.dtl_constants import DTL_EMPLOYEE, DTL_OFFICER
from workflow.ADMIN.dtl_helpers import open_dtl_checklist_detail
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def _extract_labeled_value(body: str, *labels: str) -> str:
    for label in labels:
        m = re.search(rf"{re.escape(label)}\s*:?\s*\n?\s*([^\n]+)", body, re.I)
        if m:
            val = m.group(1).strip()
            if val and label.lower() not in val.lower():
                return val
    return ""


def _extract_employee_from_body(body: str) -> tuple[str, str]:
    if DTL_EMPLOYEE not in body:
        return "", ""

    full_name = DTL_EMPLOYEE
    m = re.search(r"TK Chuyên viên\s*\(([A-Za-z0-9_]+)\)", body)
    if m:
        return full_name, m.group(1)
    m = re.search(r"TK Chuyên viên\s*\n\s*([A-Za-z0-9_]+)", body)
    if m:
        return full_name, m.group(1)
    if re.search(r"TKChuyenvien", body, re.I):
        return full_name, "TKChuyenvien"
    return full_name, ""


def _validate_employee_block(ctx: WorkflowContext) -> tuple[bool, str, dict]:
    emp_text = ui.description_field_value(ctx, "Nhân viên") or ui.description_field_value(ctx, "nhan vien")
    full_name, account_name = ui.parse_two_line_name(emp_text)

    position = ui.description_field_value(ctx, "Chức vụ") or ui.description_field_value(ctx, "chuc vu")
    department = (
        ui.description_field_value(ctx, "Đơn vị")
        or ui.description_field_value(ctx, "don vi")
        or ui.description_field_value(ctx, "Phòng ban")
    )

    body = ctx.page.locator("body").inner_text()
    if not full_name or not account_name:
        fb_full, fb_account = _extract_employee_from_body(body)
        full_name = full_name or fb_full
        account_name = account_name or fb_account
    if not position:
        position = _extract_labeled_value(body, "Chức vụ", "Chuc vu", "Position")
    if not department:
        department = _extract_labeled_value(body, "Đơn vị", "Don vi", "Phòng ban", "Phong ban", "Department")
    if not department and re.search(r"Ban\s+[\w\s]+", body):
        m = re.search(r"(Ban\s+[^\n]+)", body)
        if m:
            department = m.group(1).strip()

    meta = {
        "employeeFullName": full_name,
        "employeeAccountName": account_name,
        "position": position,
        "department": department,
    }

    if not full_name or not account_name:
        return False, "Khong du fullName + accountName trong khoi Nhan vien", meta
    if not position.strip():
        return False, "Khong hien thi Chu vu (position)", meta
    if not department.strip():
        return False, "Khong hien thi Don vi / Phong ban (department)", meta

    return True, f"{full_name} ({account_name}) — {position} / {department}", meta


def _officer_has_two_line_name(ctx: WorkflowContext) -> tuple[bool, str]:
    body = ctx.page.locator("body").inner_text()
    if DTL_OFFICER not in body:
        return False, f"Khong thay can bo [{DTL_OFFICER}] tren chi tiet/task"

    officer_text = ui.description_field_value(ctx, "Cán bộ") or ui.description_field_value(ctx, "can bo")
    if officer_text:
        full_name, account_name = ui.parse_two_line_name(officer_text)
        if full_name and account_name:
            return True, f"{full_name} ({account_name})"
        if full_name:
            return True, full_name

    m = re.search(rf"{re.escape(DTL_OFFICER)}\s*\(([A-Za-z0-9_]+)\)", body)
    if m:
        return True, f"{DTL_OFFICER} ({m.group(1)})"
    if "(" in body and DTL_OFFICER in body:
        return True, DTL_OFFICER
    return False, f"Can bo [{DTL_OFFICER}] thieu accountName tren task"


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    if not open_dtl_checklist_detail(ctx):
        return ui.fail_with_shot(
            ctx,
            "Khong mo duoc chi tiet checklist — can chay ADM-DTL-01 truoc",
            "detail_opened",
        )

    ui.shot(ctx, "employee_block")
    ok, message, meta = _validate_employee_block(ctx)
    if not ok:
        return ui.fail_with_shot(ctx, message, "employee_block", **meta)

    officer_ok, officer_label = _officer_has_two_line_name(ctx)
    if not officer_ok:
        return ui.fail_with_shot(
            ctx,
            officer_label,
            "employee_block",
            **meta,
        )

    return pass_result(
        f"Khoi nhan vien OK — {message}; can bo task: {officer_label}",
        **meta,
        officer=officer_label,
    )
