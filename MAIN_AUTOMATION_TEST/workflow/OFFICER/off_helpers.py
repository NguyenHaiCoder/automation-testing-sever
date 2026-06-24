# -*- coding: utf-8 -*-
"""Helper dùng chung OFF-LST / OFF-CFM."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui


def login_officer(ctx: WorkflowContext) -> None:
    ctx.login_as("OFFICER")


def open_officer_detail_for_template(ctx: WorkflowContext, template_name: str) -> bool:
    """Danh sách checklist → tìm tên → mở chi tiết instance OFF-LST-01."""
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, template_name)
    target = template_name.strip().lower()
    for row in ui.data_table_rows(ctx):
        if target not in row.inner_text().lower():
            continue
        row.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_officer")
            return True
        link = row.locator("a").first
        if link.count():
            link.click(timeout=8000)
            ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_officer")
            return True
    return False


def open_officer_detail(ctx: WorkflowContext) -> bool:
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return False
    if ui.open_first_list_row(ctx):
        ui.shot(ctx, "detail_from_list_officer")
        return True
    return False


def confirm_note(ctx: WorkflowContext) -> str:
    return ui.autotest_text(ctx)
