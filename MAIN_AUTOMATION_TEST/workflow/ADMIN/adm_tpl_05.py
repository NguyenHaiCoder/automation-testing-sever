# -*- coding: utf-8 -*-
"""ADM-TPL-05 — ADMIN bật/tắt trạng thái Active template Tuyển dụng."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

TEMPLATE_NAME = "Tuyển dụng"
TEMPLATE_CODE = "tuyendung"


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    tpl.goto_template_list(ctx)
    row = tpl.template_row(ctx, TEMPLATE_NAME, TEMPLATE_CODE)
    try:
        row.wait_for(state="visible", timeout=10000)
    except Exception:
        return ui.fail_with_shot(ctx, f"Khong thay template [{TEMPLATE_NAME}]", "template_list")

    was_active = tpl.is_switch_active(row)
    ui.shot(ctx, "template_active_before_toggle")
    tpl.click_status_switch(ctx, row)
    ctx.page.wait_for_timeout(800)
    now_active = tpl.is_switch_active(row)
    ui.shot(ctx, "toggle_result")

    if was_active == now_active:
        return ui.fail_with_shot(ctx, "Toggle khong doi trang thai switch", "toggle_result")

    tpl.set_template_active(ctx, TEMPLATE_NAME, was_active, TEMPLATE_CODE)
    return pass_result(
        "Toggle trang thai template OK — da khoi phuc",
        wasActive=was_active,
        nowActive=now_active,
    )
