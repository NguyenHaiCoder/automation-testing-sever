# -*- coding: utf-8 -*-
"""ADM-DTL-04 — ADMIN quay lại danh sách từ chi tiết."""
from __future__ import annotations

from workflow.ADMIN.dtl_helpers import open_dtl_checklist_detail
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    if not open_dtl_checklist_detail(ctx):
        return ui.fail_with_shot(
            ctx,
            "Khong mo duoc chi tiet checklist — can chay ADM-DTL-01 truoc",
            "detail_opened",
        )

    ui.shot(ctx, "detail_before_back")
    if ui.click_quay_lai(ctx):
        return pass_result("Quay lai danh sach checklist thanh cong", url=ctx.page.url)

    return ui.fail_with_shot(ctx, "Nut [Quay lai] khong ve duoc man danh sach", "after_quay_lai")
