# -*- coding: utf-8 -*-
"""ADM-TPL-04B — Tìm template keyword có khoảng trắng đầu: [ tuyendung]."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

# Khoảng trắng + tuyendung (không dấu) — kiểm tra FE trim/normalize keyword
TEMPLATE_SEARCH = " tuyendung"


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    tpl.goto_template_list(ctx)
    ui.search_keyword(ctx, TEMPLATE_SEARCH)
    ui.shot(ctx, "template_search_leading_space")

    body = ctx.page.locator("tbody").inner_text().lower()
    if "tuyendung" in body or "tuyển dụng" in body:
        return pass_result(
            f"Tim kiem keyword [{TEMPLATE_SEARCH!r}] van thay template Tuyen dung",
            keyword=TEMPLATE_SEARCH,
        )

    return ui.fail_with_shot(
        ctx,
        f"Khong thay template Tuyen dung sau tim kiem [{TEMPLATE_SEARCH!r}]",
        "template_search_leading_space",
        keyword=TEMPLATE_SEARCH,
    )
