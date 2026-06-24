# -*- coding: utf-8 -*-
"""Helper dùng chung OFF-LST / OFF-CFM."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui


def login_officer(ctx: WorkflowContext) -> None:
    ctx.login_as("OFFICER")


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
