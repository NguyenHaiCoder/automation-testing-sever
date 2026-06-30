# -*- coding: utf-8 -*-
"""
OFF-CFM-06 — OFFICER lọc [Quá hạn] trên danh sách checklist.

Pass: sau lọc thấy dòng có chữ «trễ» HOẶC tiến độ chưa hoàn thành (0/2, 1/3, 2/3…).
Fail: không lọc được / 0 dòng / có dòng nhưng không đủ dấu hiệu quá hạn.
"""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

STATUS_OVERDUE = "Quá hạn"


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)

    if not ui.filter_list_status(ctx, STATUS_OVERDUE):
        return ui.fail_with_shot(
            ctx,
            f"Khong chon duoc loc [Trang thai] = [{STATUS_OVERDUE}]",
            "status_filter_failed",
        )

    ui.shot(ctx, "overdue_filter_result")
    row_count = ui.data_row_count(ctx)
    if row_count == 0:
        return ui.fail_with_shot(
            ctx,
            f"Loc [{STATUS_OVERDUE}] khong co dong nao — can instance qua han trong pham vi OFFICER",
            "overdue_filter_result",
        )

    found, kind = ui.scroll_to_overdue_list_row(ctx)
    if not found:
        return ui.fail_with_shot(
            ctx,
            f"Co {row_count} dong sau loc [{STATUS_OVERDUE}] nhung khong thay "
            f"chu 'tre' hoac tien do chua hoan thanh (vd. 0/2, 1/3)",
            "overdue_filter_result",
            rowCount=row_count,
        )

    ui.shot(ctx, "overdue_row_evidence")
    ui.shot(ctx, "case_result")

    if kind == "tre":
        detail = "co chu 'tre'"
    else:
        detail = "tien do chua hoan thanh (done/total)"

    return pass_result(
        f"OFF-CFM-06 OK — loc [{STATUS_OVERDUE}] → {row_count} dong, {detail}",
        rowCount=row_count,
        evidenceKind=kind,
        statusFilter=STATUS_OVERDUE,
    )
