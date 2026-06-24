# -*- coding: utf-8 -*-
"""OFF-CFM-04 — OFFICER đổi cán bộ phụ trách task chưa confirm (BR-04)."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    if not off.open_officer_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet", "officer_detail")

    change_btn = ctx.page.locator("button:has-text('Đổi CB'), button:has-text('Đổi cán bộ')").first
    if not change_btn.count():
        return ui.fail_with_shot(ctx, "Khong thay nut Doi can bo", "officer_detail")

    change_btn.click(timeout=8000)
    ctx.page.wait_for_timeout(800)
    ui.shot(ctx, "change_officer_modal")

    opt = ctx.page.locator(".ant-select-item-option-content").first
    if opt.count():
        opt.click(timeout=5000)
        ctx.page.wait_for_timeout(400)

    save = ctx.page.locator("button:has-text('Lưu'), button:has-text('Xác nhận')").first
    if not save.count():
        return ui.fail_with_shot(ctx, "Khong thay nut Luu tren modal Doi can bo", "change_officer_modal")

    save.click(timeout=8000)
    ctx.page.wait_for_timeout(2500)
    ui.shot(ctx, "change_officer_result")

    if ui.wait_for_notice(ctx, "lỗi", "loi", "error", timeout_ms=3000):
        return ui.fail_with_shot(ctx, "Toast loi khi doi can bo", "change_officer_result")

    return pass_result("Da thuc hien flow Doi can bo (BR-04)")
