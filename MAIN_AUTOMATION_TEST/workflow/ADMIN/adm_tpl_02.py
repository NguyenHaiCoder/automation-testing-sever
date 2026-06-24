# -*- coding: utf-8 -*-
"""ADM-TPL-02 — ADMIN tạo template mới (pass khi tìm thấy automationtestver{N} trên danh sách)."""
from __future__ import annotations

from workflow.ADMIN import tpl_create
from workflow.ADMIN.tpl_helpers import next_template_name, remember_tpl02_created
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    template_name = next_template_name(ctx.case)
    ctx.login_admin()

    if not tpl_create.create_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"Khong tao duoc template [{template_name}] — form/Luu that bai",
            "template_create_form",
            templateName=template_name,
        )

    remember_tpl02_created(ctx, template_name)

    ok, detail = tpl_create.verify_template_in_list(ctx, template_name)
    if not ok:
        return ui.fail_with_shot(
            ctx,
            f"Tao xong nhung khong tim thay [{template_name}] tren danh sach — {detail}",
            "verify_template_search",
            templateName=template_name,
        )

    return pass_result(
        f"Tao template [{template_name}] thanh cong va tim thay tren danh sach (Active)",
        templateName=template_name,
        rowPreview=detail,
    )
