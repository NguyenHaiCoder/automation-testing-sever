# -*- coding: utf-8 -*-
"""ADM-LST-03 — Lọc theo khoảng ngày (checklist nằm trọn trong khoảng lọc)."""
from __future__ import annotations

from datetime import date

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

FILTER_START = date(2026, 6, 1)
FILTER_END = date(2026, 6, 30)


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.pick_date_range(
        ctx,
        year=FILTER_START.year,
        month=FILTER_START.month,
        start_day=FILTER_START.day,
        end_day=FILTER_END.day,
    )
    ui.shot(ctx, "date_filter_result")

    rows = ui.extract_checklist_date_rows(ctx)
    if not rows:
        return ui.fail_with_shot(
            ctx,
            f"Khong co dong du lieu sau loc {FILTER_START:%d/%m/%Y}–{FILTER_END:%d/%m/%Y}",
            "date_filter_result",
        )

    valid: list[str] = []
    invalid: list[str] = []
    for raw_from, raw_to, from_d, to_d in rows:
        label = f"{raw_from} → {raw_to}"
        if ui.dates_within_filter_range(from_d, to_d, FILTER_START, FILTER_END):
            valid.append(label)
        else:
            invalid.append(label)

    if invalid:
        return ui.fail_with_shot(
            ctx,
            f"Co {len(invalid)}/{len(rows)} dong NGOAI khoang "
            f"{FILTER_START:%d/%m/%Y}–{FILTER_END:%d/%m/%Y} (BE dang loc overlap?)",
            "date_filter_result",
            invalid=invalid[:8],
            validCount=len(valid),
        )

    return pass_result(
        f"{len(valid)}/{len(rows)} dong co Tu ngay/Den ngay nam tron trong "
        f"{FILTER_START:%d/%m/%Y}–{FILTER_END:%d/%m/%Y}",
        rowCount=len(rows),
        samples=valid[:5],
    )
