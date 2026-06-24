# -*- coding: utf-8 -*-
"""ADM-TPL-01 — ADMIN truy cập danh sách template."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

REQUIRED_COLUMNS = ("Mã template", "Tên template", "Mô tả", "Trạng thái", "Ngày tạo", "Chức năng")


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    tpl.goto_template_list(ctx)
    ui.shot(ctx, "template_list")

    headers = ui.table_headers(ctx)
    if not headers:
        return ui.fail_with_shot(ctx, "Khong thay bang danh sach template", "template_list")

    has_create = ctx.page.locator("button:has-text('Tạo template mới')").count() > 0
    if not has_create:
        return ui.fail_with_shot(ctx, "Khong thay button [Tao template moi]", "template_list")

    missing = [col for col in REQUIRED_COLUMNS if not any(col in h for h in headers)]
    if missing:
        return ui.fail_with_shot(
            ctx,
            f"Thieu cot tren bang template: {', '.join(missing)}",
            "template_list",
            headers=headers,
        )

    row_count = ui.data_row_count(ctx)
    return pass_result(
        f"Danh sach template OK — {row_count} dong, du cot va nut Tao template moi",
        headers=headers,
        rowCount=row_count,
    )
