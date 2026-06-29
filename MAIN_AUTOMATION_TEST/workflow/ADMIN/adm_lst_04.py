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

    if ui.is_login_page(ctx):
        return ui.fail_with_shot(
            ctx,
            "Van o man login sau khi dang nhap ADMIN — kiem tra accounts.env",
            "login_blocked",
        )

    if not ui.table_headers(ctx):
        return ui.fail_with_shot(ctx, "Khong vao duoc man [Danh sach checklist]", "list_page")

    if not ui.filter_thuc_hien_cho_employee(ctx, scope, employee):
        return ui.fail_with_shot(
            ctx,
            f"Khong chon duoc [{scope}] + [{employee}]",
            "filter_failed",
        )

    ui.shot(ctx, "filter_result")
    names = ui.extract_employee_names_from_table(ctx)
    if not names:
        return ui.fail_with_shot(
            ctx,
            f"Khong co dong nao sau loc — can nhan vien [{employee}]",
            "filter_result",
        )

    matches = [n for n in names if employee in n]
    if not matches:
        return ui.fail_with_shot(
            ctx,
            f"Co {len(names)} dong nhung khong co [{employee}]",
            "filter_result",
            samples=names[:8],
        )

    return pass_result(
        f"Loc [{scope}] + [{employee}] OK — {len(matches)}/{len(names)} dong khop",
        rows=len(names),
        matched=len(matches),
    )
