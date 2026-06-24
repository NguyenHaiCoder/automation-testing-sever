# -*- coding: utf-8 -*-
"""OFF-CFM-03 — OFFICER xác nhận task muộn — bắt buộc lý do (BR-03)."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    if not off.open_officer_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet", "officer_detail")

    late_btn = ctx.page.locator("button:has-text('Muộn')").first
    if not late_btn.count():
        return ui.fail_with_shot(ctx, "Khong co task qua han (nut Muon) — can du lieu overdue", "officer_detail")

    late_btn.click(timeout=8000)
    ctx.page.wait_for_timeout(800)
    ui.shot(ctx, "late_confirm_modal")

    reason = off.confirm_note(ctx)
    ui.fill_modal_text(ctx, reason)
    ui.confirm_modal(ctx)
    ui.shot(ctx, "off_confirm_result")

    return pass_result("OFFICER xac nhan muon voi ly do (BR-03)", reason=reason)
