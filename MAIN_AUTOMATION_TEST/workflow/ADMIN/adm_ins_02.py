# -*- coding: utf-8 -*-
"""ADM-INS-02 — Verify danh sách sau tạo (kết quả ADM-INS-01)."""
from __future__ import annotations

from workflow.ADMIN.ins_constants import CREATE_EMPLOYEE
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, CREATE_EMPLOYEE)
    ui.shot(ctx, "verify_create_list")
    names = ui.extract_employee_names_from_table(ctx)
    matches = [n for n in names if CREATE_EMPLOYEE in n]
    if not matches:
        return ui.fail_with_shot(
            ctx,
            f"Khong tim thay [{CREATE_EMPLOYEE}] trong bang sau tim kiem — can chay ADM-INS-01 truoc",
            "verify_create_list",
            totalRows=len(names),
        )
    return pass_result(
        f"Tim thay [{CREATE_EMPLOYEE}] tren danh sach ({len(matches)} dong)",
        rows=len(matches),
        totalRows=len(names),
    )
