# -*- coding: utf-8 -*-
"""OFF-LST-01 — OFFICER chỉ thấy checklist có task được giao (BR-10)."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    result = ui.assert_list_page(ctx, "OFFICER")
    if result.get("result") == "Fail":
        return result

    tpl_check = ui.officer_cannot_access_template(ctx)
    if tpl_check.get("result") == "Fail":
        return tpl_check

    ui.goto_checklist_list(ctx)
    rows = ui.data_row_count(ctx)
    ui.shot(ctx, "officer_list_scope")
    if rows == 0:
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong co checklist duoc giao — can instance co task cho officer",
            "officer_list_scope",
        )

    return pass_result(
        f"OFFICER — danh sach trong pham vi ({rows} dong), khong truy cap template admin",
        rowCount=rows,
    )
