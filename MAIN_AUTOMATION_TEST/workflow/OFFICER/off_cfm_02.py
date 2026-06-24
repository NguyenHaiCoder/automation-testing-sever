# -*- coding: utf-8 -*-
"""OFF-CFM-02 — OFFICER xác nhận task đúng hạn (BR-01)."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    if not off.open_officer_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet de xac nhan", "officer_detail")

    if not ui.click_task_confirm_on_time(ctx):
        return ui.fail_with_shot(ctx, "Khong thay nut [Dung han] tren task", "officer_detail")

    note = off.confirm_note(ctx)
    ui.fill_modal_text(ctx, note)
    ui.confirm_modal(ctx)
    ui.shot(ctx, "off_confirm_result")

    if ui.wait_for_notice(ctx, "lỗi", "loi", "error", timeout_ms=4000):
        return ui.fail_with_shot(ctx, "Toast loi sau xac nhan officer", "off_confirm_result", note=note)

    return pass_result("OFFICER xac nhan task dung han (BR-01)", note=note)
