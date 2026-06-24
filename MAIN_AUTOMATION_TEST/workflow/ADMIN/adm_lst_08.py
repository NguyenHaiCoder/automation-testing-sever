# -*- coding: utf-8 -*-
"""ADM-LST-08 — Cột Nhân viên fullName + accountName (BR-13)."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.shot(ctx, "employee_column")
    pairs = ui.extract_employee_column_pairs(ctx)
    if not pairs:
        return ui.fail_with_shot(ctx, "Khong co dong nhan vien trong bang", "employee_column")

    valid: list[str] = []
    invalid: list[str] = []
    for full_name, account_name in pairs:
        label = f"{full_name} / {account_name}"
        if full_name and account_name:
            valid.append(label)
        else:
            missing = []
            if not full_name:
                missing.append("fullName")
            if not account_name:
                missing.append("accountName")
            invalid.append(f"{label or '(trong)'} — thieu {', '.join(missing)}")

    if not invalid:
        return pass_result(
            f"Moi nhan vien co fullName + accountName ({len(valid)} dong)",
            samples=valid[:6],
        )
    return ui.fail_with_shot(
        ctx,
        f"{len(invalid)}/{len(pairs)} dong khong du 2 dong ten hoac bi trong",
        "employee_column",
        invalid=invalid[:8],
        validCount=len(valid),
    )
