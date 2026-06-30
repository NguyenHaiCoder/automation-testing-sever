# -*- coding: utf-8 -*-
"""
OFF-LST-03 — OFFICER lọc checklist theo khoảng ngày 26/06/2026–29/06/2026 (boundary).

Pass: mọi dòng có Từ ngày / Đến ngày nằm trọn trong 26/06–29/06.
Fail: có dòng vượt biên (vd. Đến ngày 30/06/2026 > 29/06/2026) — BUG BE overlap.
"""
from __future__ import annotations

from datetime import date

from workflow.OFFICER import off_constants as oc
from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

FILTER_START = date(2026, 6, 26)
FILTER_END = date(2026, 6, 29)


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)

    ui.pick_date_range(
        ctx,
        year=FILTER_START.year,
        month=FILTER_START.month,
        start_day=FILTER_START.day,
        end_day=FILTER_END.day,
    )
    ui.shot(ctx, "date_filter_result_officer")

    rows = ui.extract_checklist_date_rows(ctx)
    if not rows:
        return pass_result(
            f"Loc {oc.DATE_FILTER_START}–{oc.DATE_FILTER_END} OK — 0 dong, "
            f"khong vi pham bien {oc.DATE_FILTER_END}",
            rowCount=0,
            dateRange=f"{oc.DATE_FILTER_START}-{oc.DATE_FILTER_END}",
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
        boundary_hint = ""
        for _, raw_to, _, to_d in rows:
            if to_d and to_d > FILTER_END:
                boundary_hint = (
                    f" — vi pham bien: Den ngay {raw_to} > {oc.DATE_FILTER_END}"
                )
                break
        return ui.fail_with_shot(
            ctx,
            f"Boundary FAIL: {len(invalid)}/{len(rows)} dong NGOAI khoang "
            f"{oc.DATE_FILTER_START}–{oc.DATE_FILTER_END}{boundary_hint}",
            "date_filter_result_officer",
            invalid=invalid[:8],
            validCount=len(valid),
        )

    return pass_result(
        f"OFFICER loc {oc.DATE_FILTER_START}–{oc.DATE_FILTER_END} OK — "
        f"{len(valid)}/{len(rows)} dong nam tron trong khoang (boundary pass)",
        rowCount=len(rows),
        dateRange=f"{oc.DATE_FILTER_START}-{oc.DATE_FILTER_END}",
        samples=valid[:5],
    )
