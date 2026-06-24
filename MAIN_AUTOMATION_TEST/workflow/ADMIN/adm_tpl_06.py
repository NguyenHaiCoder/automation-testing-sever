# -*- coding: utf-8 -*-
"""ADM-TPL-06 — ADMIN xem chi tiết template."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

TEMPLATE_NAME = "Tuyển dụng"


def _detail_opened(ctx: WorkflowContext) -> bool:
    for sel in (".ant-modal:visible", ".ant-drawer-open", ".ant-drawer:not(.ant-drawer-hidden)"):
        if ctx.page.locator(sel).count():
            return True
    body = ctx.page.locator("body").inner_text().lower()
    markers = ("đầu việc", "dau viec", "tên mục", "ten muc", "section", "task", "mục")
    return any(m in body for m in markers) and TEMPLATE_NAME.lower() in body.lower()


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    tpl.goto_template_list(ctx)
    row = tpl.template_row(ctx, TEMPLATE_NAME)
    if not row.count():
        return ui.fail_with_shot(ctx, f"Khong thay template [{TEMPLATE_NAME}]", "template_list")

    tpl.open_template_view(ctx, TEMPLATE_NAME)
    ui.shot(ctx, "template_view")

    if _detail_opened(ctx):
        return pass_result(f"Mo xem chi tiet template [{TEMPLATE_NAME}] OK")
    return ui.fail_with_shot(ctx, "Khong mo duoc chi tiet/xem template", "template_view")
