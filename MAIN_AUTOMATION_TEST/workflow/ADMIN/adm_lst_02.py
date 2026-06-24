# -*- coding: utf-8 -*-
"""ADM-LST-02 — Tìm kiếm theo Keyword."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, "test")
    ui.shot(ctx, "case_result")
    rows = ui.data_row_count(ctx)
    return pass_result(f"Tim kiem Keyword OK — {rows} dong", keyword="test")
