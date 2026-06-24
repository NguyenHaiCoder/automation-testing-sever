# -*- coding: utf-8 -*-
"""
OFF-LST-03 — OFFICER lọc checklist theo khoảng ngày 01/06/2026–30/06/2026.

Phụ thuộc OFF-LST-01: sau lọc vẫn thấy record checklist trong phạm vi quyền.
"""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.OFFICER import off_lst_prep as prep
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

FILTER_YEAR = 2026
FILTER_MONTH = 6
FILTER_START_DAY = 1
FILTER_END_DAY = 30


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)

    ui.pick_date_range(
        ctx,
        year=FILTER_YEAR,
        month=FILTER_MONTH,
        start_day=FILTER_START_DAY,
        end_day=FILTER_END_DAY,
    )
    ui.shot(ctx, "date_filter_result_officer")

    rows = ui.data_row_count(ctx)
    if rows == 0:
        return ui.fail_with_shot(
            ctx,
            "Khong co dong sau loc 01/06/2026–30/06/2026 — can OFF-LST-01 truoc",
            "date_filter_result_officer",
        )

    template_name = prep.resolve_lst01_template(ctx)
    if template_name and not prep.list_shows_checklist(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"Loc ngay OK nhung khong thay checklist OFF-LST-01 [{template_name}]",
            "date_filter_result_officer",
            rowCount=rows,
        )

    return pass_result(
        f"OFFICER loc 01/06/2026–30/06/2026 OK ({rows} dong trong pham vi quyen)",
        rowCount=rows,
        dateRange="01/06/2026-30/06/2026",
    )
