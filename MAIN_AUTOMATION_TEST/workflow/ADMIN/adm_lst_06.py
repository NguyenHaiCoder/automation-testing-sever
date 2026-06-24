# -*- coding: utf-8 -*-
"""ADM-LST-06 — Cột tiến độ done/total."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    ui.goto_checklist_list(ctx)
    ui.shot(ctx, "progress_column")
    if ui.progress_pattern_in_table(ctx):
        return pass_result("Cot Tien do hien dang done/total")
    return ui.fail_with_shot(ctx, "Khong thay dinh dang tien do d/t trong bang", "progress_column")
