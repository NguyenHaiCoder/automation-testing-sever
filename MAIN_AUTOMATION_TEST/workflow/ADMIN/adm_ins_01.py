# -*- coding: utf-8 -*-
"""ADM-INS-01 — Tạo checklist instance."""
from __future__ import annotations

from workflow.ADMIN import create_checklist
from workflow.ADMIN.ins_constants import CREATE_EMPLOYEE, CREATE_OFFICER
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def _verify_employee_only_in_list(ctx: WorkflowContext, expected_name: str) -> dict:
    ui.search_keyword(ctx, expected_name)
    ui.shot(ctx, "verify_create_list")
    names = ui.extract_employee_names_from_table(ctx)
    if not names:
        return ui.fail_with_shot(
            ctx,
            f"Khong co dong nao sau tim [{expected_name}] — tao checklist that bai hoac chua dong bo",
            "verify_create_list",
        )
    others = [n for n in names if expected_name not in n]
    if others:
        return ui.fail_with_shot(
            ctx,
            f"Tim thay [{expected_name}] nhung con nhan vien khac trong bang",
            "verify_create_list",
            otherEmployees=others[:8],
            totalRows=len(names),
        )
    return pass_result(
        f"Tao checklist thanh cong — danh sach chi co [{expected_name}]",
        rows=len(names),
    )


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    create_checklist.open_modal(ctx)

    if not create_checklist.fill_form(
        ctx,
        officer_name=CREATE_OFFICER,
        employee_name=CREATE_EMPLOYEE,
    ):
        create_checklist.close_modal(ctx)
        return ui.fail_with_shot(
            ctx,
            f"Khong dien duoc form Tao checklist — CB [{CREATE_OFFICER}], NV [{CREATE_EMPLOYEE}]",
            "create_checklist_modal",
        )

    ok, reason = create_checklist.submit(ctx)
    if not ok:
        create_checklist.close_modal(ctx)
        if reason == "duplicate":
            return ui.fail_with_shot(
                ctx,
                f"Template + nhan vien [{CREATE_EMPLOYEE}] da ton tai (BR-06) — doi template/nhan vien",
                "create_result",
            )
        return ui.fail_with_shot(ctx, "Khong tao duoc checklist — nut Tao/validate loi", "create_result")

    ui.goto_checklist_list(ctx)
    return _verify_employee_only_in_list(ctx, CREATE_EMPLOYEE)
