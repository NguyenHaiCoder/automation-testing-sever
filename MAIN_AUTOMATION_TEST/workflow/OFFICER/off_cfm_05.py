# -*- coding: utf-8 -*-
"""OFF-CFM-05 — OFFICER hoàn tác xác nhận trong 60 phút (BR-02)."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    if not off.open_officer_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet", "officer_detail")

    undo = ctx.page.locator("button:has-text('Hoàn tác'), button:has-text('Undo')").first
    if not undo.count():
        return ui.fail_with_shot(
            ctx,
            "Khong thay nut Hoan tac — can officer da confirm trong 60 phut (chay OFF-CFM-02 truoc)",
            "officer_detail",
        )

    undo.click(timeout=8000)
    ctx.page.wait_for_timeout(1200)
    confirm = ctx.page.locator(
        ".ant-modal button:has-text('Xác nhận'), .ant-popconfirm button:has-text('Xác nhận')"
    ).last
    if confirm.count():
        confirm.click(timeout=5000)
        ctx.page.wait_for_timeout(1500)

    ui.shot(ctx, "undo_result")

    if ui.task_action_visible(ctx, "Đúng hạn"):
        return pass_result("Hoan tac officer OK — nut Dung han hien lai (BR-02)")

    if not ctx.page.locator("button:has-text('Hoàn tác'), button:has-text('Undo')").count():
        return pass_result("Hoan tac officer OK — nut Hoan tac da bien mat (BR-02)")

    return ui.fail_with_shot(ctx, "Hoan tac khong thay doi trang thai task", "undo_result")
