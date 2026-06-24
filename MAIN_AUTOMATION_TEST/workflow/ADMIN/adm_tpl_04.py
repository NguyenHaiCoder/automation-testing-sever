# -*- coding: utf-8 -*-
"""ADM-TPL-04 — ADMIN tìm kiếm template theo keyword tuyendung."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

TEMPLATE_SEARCH = "tuyendung"


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    tpl.goto_template_list(ctx)
    ui.search_keyword(ctx, TEMPLATE_SEARCH)
    ui.shot(ctx, "template_search_result")

    body = ctx.page.locator("tbody").inner_text().lower()
    if TEMPLATE_SEARCH in body or "tuyển dụng" in body:
        return pass_result(f"Tim kiem template [{TEMPLATE_SEARCH}] OK", keyword=TEMPLATE_SEARCH)

    return ui.fail_with_shot(
        ctx,
        "Khong thay template Tuyen dung sau tim kiem",
        "template_search_result",
        keyword=TEMPLATE_SEARCH,
    )
