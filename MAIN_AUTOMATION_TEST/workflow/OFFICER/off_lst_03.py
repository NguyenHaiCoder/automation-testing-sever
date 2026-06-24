# -*- coding: utf-8 -*-
"""OFF-LST-03 — OFFICER lọc checklist theo khoảng ngày."""
from __future__ import annotations

from datetime import date

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return ui.fail_with_shot(ctx, "Khong co dong de loc ngay — can OFF-LST-01", "date_filter_result_officer")

    today = date.today()
    ui.pick_date_range(
        ctx,
        year=today.year,
        month=today.month,
        start_day=1,
        end_day=min(today.day, 28) if today.day > 1 else today.day,
    )
    ui.shot(ctx, "date_filter_result_officer")
    return pass_result(
        "OFFICER loc khoang ngay OK",
        rowCount=ui.data_row_count(ctx),
    )
