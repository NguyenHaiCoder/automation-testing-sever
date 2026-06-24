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
    if not names:
        return ui.fail_with_shot(
            ctx,
            f"Khong co dong nao sau tim [{CREATE_EMPLOYEE}] — can chay ADM-INS-01 truoc",
            "verify_create_list",
        )
    others = [n for n in names if CREATE_EMPLOYEE not in n]
    if others:
        return ui.fail_with_shot(
            ctx,
            f"Tim thay [{CREATE_EMPLOYEE}] nhung con nhan vien khac trong bang",
            "verify_create_list",
            otherEmployees=others[:8],
            totalRows=len(names),
        )
    return pass_result(
        f"Tao checklist thanh cong — danh sach chi co [{CREATE_EMPLOYEE}]",
        rows=len(names),
    )
