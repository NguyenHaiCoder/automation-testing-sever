# -*- coding: utf-8 -*-
"""OFF-LST-04 — OFFICER làm mới danh sách."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)
    before = ui.data_row_count(ctx)
    ui.click_refresh(ctx)
    ui.shot(ctx, "after_refresh_officer")
    headers = ui.table_headers(ctx)
    if not headers:
        return ui.fail_with_shot(ctx, "Khong thay bang sau lam moi", "after_refresh_officer")

    return pass_result(
        f"OFFICER lam moi danh sach OK ({before} -> {ui.data_row_count(ctx)} dong)",
        rowCount=ui.data_row_count(ctx),
    )
