# -*- coding: utf-8 -*-
"""OFF-LST-02 — OFFICER tìm kiếm checklist theo Keyword."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.OFFICER.off_constants import SEARCH_KEYWORD
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return ui.fail_with_shot(ctx, "Khong co dong de tim kiem — can OFF-LST-01", "search_filled")

    ui.search_keyword(ctx, SEARCH_KEYWORD)
    ui.shot(ctx, "search_result_officer")
    headers = ui.table_headers(ctx)
    if not headers:
        return ui.fail_with_shot(ctx, "Khong thay bang sau tim kiem", "search_result_officer")

    return pass_result(
        f"OFFICER tim kiem [{SEARCH_KEYWORD}] OK — ket qua trong pham vi quyen",
        keyword=SEARCH_KEYWORD,
        rowCount=ui.data_row_count(ctx),
    )
