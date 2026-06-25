# -*- coding: utf-8 -*-
"""Tạo template mới + kiểm tra hiển thị trên danh sách (ADM-TPL-02 / ADM-TPL-03)."""
from __future__ import annotations

import re

from playwright.sync_api import Locator

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl

DEFAULT_DURATION_DAYS = 7
DEFAULT_OFFICER = "Quyền Phạm Năng"


def _fill_input_verified(
    ctx: WorkflowContext,
    inp: Locator,
    value: str,
    label: str,
) -> bool:
    return tpl.fill_input_verified(ctx, inp, value, label)


def _fill_duration_days(ctx: WorkflowContext, modal: Locator, index: int, days: int) -> None:
    candidates = modal.locator(
        'input[placeholder*="ngày" i], input[placeholder*="ngay" i], '
        'input[placeholder*="duration" i], input[type="number"]'
    )
    if candidates.count() > index:
        inp = candidates.nth(index)
        try:
            if inp.is_visible():
                _fill_input_verified(ctx, inp, str(days), f"DurationDays #{index + 1}")
        except Exception:
            pass


def _assign_default_officer(ctx: WorkflowContext, modal: Locator, index: int) -> None:
    selects = modal.locator(".ant-form-item").filter(
        has_text=re.compile(r"Cán bộ mặc định|can bo mac dinh|DefaultOfficer", re.I)
    )
    if selects.count() <= index:
        return
    sel = selects.nth(index).locator(".ant-select").first
    if not sel.count():
        return
    try:
        sel.click(timeout=5000)
        ctx.page.wait_for_timeout(200)
        opt = ctx.page.locator(".ant-select-item-option-content").filter(has_text=DEFAULT_OFFICER).first
        if opt.count():
            opt.click(timeout=5000)
            ctx.page.wait_for_timeout(150)
    except Exception:
        ctx.log(f"Khong gan duoc can bo mac dinh cho task #{index + 1}", "WARN")


def _fill_first_section(ctx: WorkflowContext, modal: Locator, section_name: str) -> bool:
    section_items = modal.locator(".ant-form-item").filter(has_text="Tên mục")
    if section_items.count() == 0:
        ctx.log("Khong thay o Ten muc", "WARN")
        return False

    section_item = section_items.first
    section_item.scroll_into_view_if_needed()
    name_inp = section_item.locator("input").first
    if not _fill_input_verified(ctx, name_inp, section_name, "Ten muc"):
        return False

    task_inputs = modal.locator('input[placeholder*="đầu việc" i], input[placeholder*="dau viec" i]')
    if task_inputs.count() == 0:
        ctx.log("Khong thay o mo ta dau viec", "WARN")
        return False
    task_text = f"{section_name} — task 1"
    if not _fill_input_verified(ctx, task_inputs.first, task_text, "Dau viec"):
        return False

    _fill_duration_days(ctx, modal, 0, DEFAULT_DURATION_DAYS)
    _assign_default_officer(ctx, modal, 0)
    return True


def create_template(ctx: WorkflowContext, template_name: str) -> bool:
    tpl.goto_template_list(ctx)
    ui.click_button(ctx, "Tạo template mới")
    modal = ctx.page.locator(".ant-modal").filter(has_text=re.compile(r"Tạo template", re.I))
    modal.wait_for(timeout=10000)

    text_inputs = modal.locator("input[type='text'], input:not([type])")
    if text_inputs.count() >= 2:
        if not _fill_input_verified(ctx, text_inputs.nth(0), template_name, "Ma template"):
            return False
        if not _fill_input_verified(ctx, text_inputs.nth(1), template_name, "Ten template"):
            return False
    note = modal.locator("textarea").first
    if note.count():
        if not _fill_input_verified(ctx, note, template_name, "Mo ta template"):
            return False

    if not _fill_first_section(ctx, modal, template_name):
        return False

    ui.shot(ctx, "template_create_form")
    submit = modal.locator("button:has-text('Lưu'), button:has-text('Tạo')").first
    if not submit.count():
        return False
    submit.click(timeout=8000)
    tpl.wait_template_modal_saved(ctx, modal)
    ui.shot(ctx, "template_create_result")

    body = ctx.page.locator("body").inner_text().lower()
    if "thành công" in body or "thanh cong" in body:
        return True
    try:
        modal.wait_for(state="hidden", timeout=8000)
        return True
    except Exception:
        return "/template" in ctx.page.url


def verify_template_in_list(ctx: WorkflowContext, template_name: str) -> tuple[bool, str]:
    """Tìm kiếm đúng keyword template_name — phải có dòng khớp tên/mã và Active."""
    tpl.goto_template_list(ctx)
    ui.search_keyword(ctx, template_name)
    ui.shot(ctx, "verify_template_search")

    rows = ui.data_table_rows(ctx)
    if not rows:
        return False, f"Khong co dong nao sau tim kiem [{template_name}]"

    target = template_name.strip().lower()
    for row in rows:
        text = row.inner_text()
        low = text.lower()
        if target not in low:
            continue
        try:
            if tpl.is_switch_active(row):
                return True, text[:120]
        except Exception:
            pass
        if "active" in low:
            return True, text[:120]
        return False, f"Tim thay [{template_name}] nhung trang thai khong Active"

    return False, f"Co {len(rows)} dong nhung khong khop chinh xac [{template_name}]"
