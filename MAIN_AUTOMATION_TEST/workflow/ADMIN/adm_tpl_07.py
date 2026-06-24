# -*- coding: utf-8 -*-
"""ADM-TPL-07 — ADMIN sửa template → đổi tên automationtestver{N}."""
from __future__ import annotations

from workflow.ADMIN.tpl_helpers import next_template_name, remember_tpl07_edited
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result

EDIT_CANDIDATES = ("Mẫu Onboarding", "Tuyển dụng")


def _fill_template_name(ctx: WorkflowContext, new_name: str) -> bool:
    root = ctx.page.locator(".ant-modal:visible, .ant-drawer-open").last
    if not root.count():
        root = ctx.page.locator("body")

    for item in root.locator(".ant-form-item").all():
        try:
            label_el = item.locator(".ant-form-item-label, label").first
            if not label_el.count():
                continue
            label = label_el.inner_text().lower()
            if "tên template" not in label and "ten template" not in label:
                continue
            inp = item.locator("input").first
            inp.click(timeout=5000)
            inp.fill("")
            inp.fill(new_name)
            ctx.page.wait_for_timeout(400)
            return True
        except Exception:
            continue

    for inp in root.locator("input[type='text']").all()[:6]:
        try:
            if inp.is_visible():
                inp.click()
                inp.fill(new_name)
                ctx.page.wait_for_timeout(400)
                return True
        except Exception:
            continue
    return False


def _open_edit_form(ctx: WorkflowContext) -> bool:
    for name in EDIT_CANDIDATES:
        if tpl.open_template_edit(ctx, name):
            return True
    return False


def run(ctx: WorkflowContext) -> dict:
    new_name = next_template_name(ctx.case)
    ctx.login_admin()
    tpl.goto_template_list(ctx)

    if not _open_edit_form(ctx):
        return ui.fail_with_shot(ctx, "Khong mo duoc form sua template", "template_edit")

    if not _fill_template_name(ctx, new_name):
        return ui.fail_with_shot(
            ctx,
            f"Khong dien duoc ten template [{new_name}]",
            "template_edit",
            templateName=new_name,
        )

    ui.shot(ctx, "template_edit_filled")
    save = ctx.page.locator("button:has-text('Lưu')").first
    if not save.count():
        return ui.fail_with_shot(ctx, "Khong thay nut [Luu]", "template_edit")

    save.click(timeout=8000)
    ctx.page.wait_for_timeout(3000)
    ui.shot(ctx, "template_edit_result")

    body = ctx.page.locator("body").inner_text().lower()
    saved = "thành công" in body or "thanh cong" in body
    if not saved:
        try:
            ctx.page.locator(".ant-modal:visible").wait_for(state="hidden", timeout=5000)
            saved = True
        except Exception:
            saved = False

    if not saved:
        return ui.fail_with_shot(
            ctx,
            f"Luu template [{new_name}] that bai — khong co phan hoi thanh cong",
            "template_edit_result",
            templateName=new_name,
        )

    remember_tpl07_edited(ctx, new_name)
    return pass_result(f"Sua template thanh cong — ten moi [{new_name}]", templateName=new_name)
