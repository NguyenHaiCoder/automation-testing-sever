# -*- coding: utf-8 -*-
"""ADM-TPL-03 — Sau tạo template, tìm đúng automationtestver{N} trên danh sách."""
from __future__ import annotations

from workflow.ADMIN import tpl_create
from workflow.ADMIN.tpl_helpers import resolve_tpl02_template_name
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    template_name = resolve_tpl02_template_name(ctx)
    if not template_name:
        return ui.fail_with_shot(
            ctx,
            "Khong xac dinh duoc template ADM-TPL-02 — chay ADM-TPL-02 truoc",
            "verify_template_search",
        )

    ctx.login_admin()
    ok, detail = tpl_create.verify_template_in_list(ctx, template_name)
    if not ok:
        return ui.fail_with_shot(
            ctx,
            f"Khong tim thay [{template_name}] tren danh sach — {detail}",
            "verify_template_search",
            templateName=template_name,
        )

    return pass_result(
        f"Tim thay template [{template_name}] — ma/ten/trang thai dung",
        templateName=template_name,
        rowPreview=detail,
    )
