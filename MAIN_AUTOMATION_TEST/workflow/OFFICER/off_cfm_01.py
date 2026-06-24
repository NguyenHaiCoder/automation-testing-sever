# -*- coding: utf-8 -*-
"""OFF-CFM-01 — OFFICER mở chi tiết checklist có task được giao."""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    off.login_officer(ctx)
    if not off.open_officer_detail(ctx):
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong co instance/task de mo chi tiet — can du lieu test",
            "officer_detail",
        )

    ui.shot(ctx, "officer_detail")
    has_confirm = ui.task_action_visible(ctx, "Đúng hạn") or ui.task_action_visible(ctx, "Xác nhận")
    has_change = ui.task_action_visible(ctx, "Đổi CB") or ui.task_action_visible(ctx, "Đổi cán bộ")
    if has_confirm or has_change:
        return pass_result("Chi tiet co task voi nut Xac nhan / Doi can bo")

    return ui.fail_with_shot(ctx, "Khong thay nut thao tac task tren chi tiet", "officer_detail")
