# -*- coding: utf-8 -*-
"""ADM-LST-03 — Lọc theo khoảng ngày."""
from __future__ import annotations

from datetime import date

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def _dates_within_filter(
    from_d: date | None,
    to_d: date | None,
    filter_start: date,
    filter_end: date,
) -> bool:
    if not from_d or not to_d:
        return False
    return filter_start <= from_d <= filter_end and filter_start <= to_d <= filter_end


def run(ctx: WorkflowContext) -> dict:
    filter_start = date(2026, 6, 1)
    filter_end = date(2026, 6, 30)

    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.pick_date_range(ctx, year=2026, month=6, start_day=1, end_day=30)
    ui.shot(ctx, "date_filter_result")

    rows = ui.extract_checklist_date_rows(ctx)
    if not rows:
        return ui.fail_with_shot(
            ctx,
            f"Khong co dong du lieu sau loc {filter_start:%d/%m/%Y}–{filter_end:%d/%m/%Y}",
            "date_filter_result",
        )

    matched: list[str] = []
    invalid: list[str] = []
    for raw_from, raw_to, from_d, to_d in rows:
        label = f"{raw_from} → {raw_to}"
        if _dates_within_filter(from_d, to_d, filter_start, filter_end):
            matched.append(label)
        else:
            invalid.append(label)

    if matched:
        return pass_result(
            f"{len(matched)} dong co Tu ngay/Den ngay trong "
            f"{filter_start:%d/%m/%Y}–{filter_end:%d/%m/%Y}",
            matched=matched,
            invalidCount=len(invalid),
        )

    return ui.fail_with_shot(
        ctx,
        f"Khong co dong nao co Tu ngay/Den ngay trong "
        f"{filter_start:%d/%m/%Y}–{filter_end:%d/%m/%Y}",
        "date_filter_result",
        samples=invalid[:8],
    )
