# -*- coding: utf-8 -*-
"""Helper mở chi tiết checklist từ dữ liệu ADM-DTL-01 (automationtestver*)."""
from __future__ import annotations

from playwright.sync_api import Locator

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui

SEARCH_KEY = "automationtestver"

_CANCELLED_MARKERS = ("đã hủy", "da huy", "cancelled", "hủy bỏ", "huy bo")


def _is_cancelled_row(row_text: str) -> bool:
    low = row_text.lower()
    return any(m in low for m in _CANCELLED_MARKERS)


def _open_row_detail(ctx: WorkflowContext, row: Locator) -> bool:
    row.click(timeout=8000)
    ctx.page.wait_for_timeout(2000)
    if ui.is_detail_page(ctx):
        return True

    link = row.locator("a[href*='/hrm/checklist/']").first
    if link.count():
        href = link.get_attribute("href")
        if href and ui.goto_checklist_detail(ctx, href):
            return True
        link.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            return True

    return False


def open_dtl_checklist_detail(ctx: WorkflowContext, *, skip_cancelled: bool = False) -> bool:
    """Mở chi tiết checklist automationtestver — tùy chọn bỏ qua dòng đã hủy."""
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, SEARCH_KEY)
    if ui.data_row_count(ctx) == 0:
        ui.goto_checklist_list(ctx)
        if ui.data_row_count(ctx) == 0:
            return False
        ctx.log("Khong tim thay automationtestver — fallback dong dau tien", "WARN")

    rows = ui.data_table_rows(ctx)
    candidates = rows if not skip_cancelled else [r for r in rows if not _is_cancelled_row(r.inner_text())]
    if not candidates:
        return False

    for row in candidates:
        if _open_row_detail(ctx, row):
            ui.shot(ctx, "detail_opened")
            return True

    href = ui.first_row_detail_href(ctx)
    if href and ui.goto_checklist_detail(ctx, href):
        ui.shot(ctx, "detail_opened")
        return True
    return False
