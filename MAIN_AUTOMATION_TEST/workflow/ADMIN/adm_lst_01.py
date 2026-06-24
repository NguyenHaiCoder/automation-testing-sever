# -*- coding: utf-8 -*-
"""ADM-LST-01 — ADMIN xem danh sách checklist."""
from __future__ import annotations

from workflow.common import WorkflowContext


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    from workflow.helpers import checklist_ui as ui

    return ui.assert_list_page(ctx, "ADMIN", require_create=True)
