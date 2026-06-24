# -*- coding: utf-8 -*-
"""ADM-LST-04 — Lọc Thực hiện cho NV."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    scope = "Thực hiện cho NV"
    employee = "Quyền Phạm Năng"

    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    if not ui.filter_thuc_hien_cho_employee(ctx, scope, employee):
        return ui.fail_with_shot(ctx, f"Khong chon duoc [{scope}] + [{employee}]")

    ui.shot(ctx, "filter_result")
    names = ui.extract_employee_names_from_table(ctx)
    if not names:
        return ui.fail_with_shot(ctx, f"Khong co dong nao sau loc — can nhan vien [{employee}]", "filter_result")

    others = [n for n in names if employee not in n]
    if others:
        return ui.fail_with_shot(
            ctx,
            f"Bang con {len(others)} dong nhan vien khac — can chi [{employee}]",
            "filter_result",
            otherEmployees=others[:8],
            totalRows=len(names),
        )
    return pass_result(f"Bang chi hien thi nhan vien [{employee}]", rows=len(names))
