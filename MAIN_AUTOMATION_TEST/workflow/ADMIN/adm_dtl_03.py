# -*- coding: utf-8 -*-
"""ADM-DTL-03 — ADMIN hủy checklist instance (BR-07)."""
from __future__ import annotations

from workflow.ADMIN.dtl_helpers import open_dtl_checklist_detail
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result

CANCEL_ERROR_MARKERS = (
    "Có lỗi xảy ra khi hủy checklist",
    "co loi xay ra khi huy checklist",
    "An error occurred",
)


def _cancel_modal_still_open(ctx: WorkflowContext) -> bool:
    modal = ctx.page.locator(".ant-modal:visible").filter(has_text="Lý do hủy")
    return modal.count() > 0


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    if not open_dtl_checklist_detail(ctx, skip_cancelled=True):
        return ui.fail_with_shot(
            ctx,
            "Khong mo duoc chi tiet checklist chua huy — can chay ADM-DTL-01 truoc",
            "detail_opened",
        )

    detail_btn = ctx.page.locator("button:has-text('Hủy checklist')").first
    if not detail_btn.count():
        return ui.fail_with_shot(ctx, "Khong thay nut [Huy checklist] tren chi tiet", "detail_opened")
    detail_btn.click(timeout=8000)
    ctx.page.wait_for_timeout(800)
    ui.shot(ctx, "cancel_modal")

    reason = ui.autotest_text(ctx)
    ui.fill_modal_text(ctx, reason)
    ui.confirm_cancel_checklist_modal(ctx)

    error_text = ui.wait_for_notice(ctx, *CANCEL_ERROR_MARKERS, timeout_ms=12000)
    ui.shot(ctx, "after_cancel")

    if error_text:
        return ui.fail_with_shot(
            ctx,
            f"Toast loi khi huy checklist: [{error_text}]",
            "cancel_error_toast",
            reason=reason,
        )

    if _cancel_modal_still_open(ctx):
        return ui.fail_with_shot(
            ctx,
            "Huy checklist that bai — modal [Ly do huy] van mo sau khi xac nhan",
            "cancel_modal",
            reason=reason,
        )

    return pass_result(
        "Huy checklist khong co toast loi — flow hoan tat",
        reason=reason,
    )
