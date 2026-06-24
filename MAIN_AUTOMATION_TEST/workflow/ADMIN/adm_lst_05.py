# -*- coding: utf-8 -*-
"""ADM-LST-05 — Làm mới danh sách."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    before = ui.pagination_text(ctx)
    ui.click_refresh(ctx)
    after = ui.pagination_text(ctx)
    ui.shot(ctx, "case_result")
    return pass_result("Lam moi danh sach OK", before=before, after=after)
