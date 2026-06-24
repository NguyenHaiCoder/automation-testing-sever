# -*- coding: utf-8 -*-
"""ADM-LST-07 — Mở chi tiết từ danh sách."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return ui.fail_with_shot(ctx, "Khong co dong de mo chi tiet")
    if not ui.open_first_list_row(ctx):
        return ui.fail_with_shot(ctx, "Khong mo duoc chi tiet tu danh sach")
    ui.shot(ctx, "detail_from_list")
    if ui.is_detail_page(ctx):
        return pass_result("Mo chi tiet checklist thanh cong", url=ctx.page.url)
    return ui.fail_with_shot(ctx, f"URL khong phai chi tiet: {ctx.page.url}", "detail_from_list")
