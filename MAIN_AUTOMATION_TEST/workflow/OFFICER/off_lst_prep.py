# -*- coding: utf-8 -*-
"""Chuẩn bị dữ liệu ADMIN cho OFF-LST-01 (template + checklist)."""
from __future__ import annotations

import re

from playwright.sync_api import Locator

from workflow.ADMIN import create_checklist
from workflow.ADMIN.tpl_helpers import allocate_next_template_version
from workflow.OFFICER.off_constants import TEMPLATE_SUFFIX
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl

DEFAULT_DURATION_DAYS = 7


def next_assignees_template_name() -> str:
    n = allocate_next_template_version()
    return f"automationtestver{n}{TEMPLATE_SUFFIX}"


def _fill_input_verified(ctx: WorkflowContext, inp: Locator, value: str, label: str) -> bool:
    inp.scroll_into_view_if_needed()
    inp.click(timeout=8000)
    inp.fill("")
    ctx.page.wait_for_timeout(350)
    inp.type(value, delay=40)
    ctx.page.wait_for_timeout(500)
    try:
        actual = inp.input_value().strip()
    except Exception:
        actual = (inp.get_attribute("value") or "").strip()
    if actual != value.strip():
        inp.fill(value)
        ctx.page.wait_for_timeout(500)
        try:
            actual = inp.input_value().strip()
        except Exception:
            actual = (inp.get_attribute("value") or "").strip()
    if actual != value.strip():
        ctx.log(f"{label}: gia tri khong khop — can [{value}], co [{actual}]", "WARN")
        return False
    return True


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


def _assign_default_officer(ctx: WorkflowContext, modal: Locator, index: int, officer_name: str) -> None:
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
        ctx.page.wait_for_timeout(500)
        opt = ctx.page.locator(".ant-select-item-option-content").filter(has_text=officer_name).first
        if opt.count():
            opt.click(timeout=5000)
            ctx.page.wait_for_timeout(400)
    except Exception:
        ctx.log(f"Khong gan duoc can bo mac dinh cho task #{index + 1}", "WARN")


def _fill_task(ctx: WorkflowContext, modal: Locator, index: int, section_name: str) -> bool:
    task_inputs = modal.locator('input[placeholder*="đầu việc" i], input[placeholder*="dau viec" i]')
    if task_inputs.count() <= index:
        ctx.log(f"Khong du o dau viec #{index + 1}", "WARN")
        return False
    task_text = f"{section_name} — task {index + 1}"
    if not _fill_input_verified(ctx, task_inputs.nth(index), task_text, f"Dau viec #{index + 1}"):
        return False
    _fill_duration_days(ctx, modal, index, DEFAULT_DURATION_DAYS)
    return True


def create_template_two_tasks(ctx: WorkflowContext, template_name: str, default_officer: str) -> bool:
    tpl.goto_template_list(ctx)
    ui.click_button(ctx, "Tạo template mới")
    modal = ctx.page.locator(".ant-modal").filter(has_text=re.compile(r"Tạo template", re.I))
    modal.wait_for(timeout=10000)

    code = template_name.replace(" ", "_").lower()[:48]
    text_inputs = modal.locator("input[type='text'], input:not([type])")
    if text_inputs.count() >= 2:
        if not _fill_input_verified(ctx, text_inputs.nth(0), code, "Ma template"):
            return False
        if not _fill_input_verified(ctx, text_inputs.nth(1), template_name, "Ten template"):
            return False
    note = modal.locator("textarea").first
    if note.count():
        _fill_input_verified(ctx, note, template_name, "Ghi chu template")

    section_items = modal.locator(".ant-form-item").filter(has_text="Tên mục")
    if section_items.count() == 0:
        return False
    section_name = f"{template_name} — muc 1"
    name_inp = section_items.first.locator("input").first
    if not _fill_input_verified(ctx, name_inp, section_name, "Ten muc"):
        return False

    if not _fill_task(ctx, modal, 0, section_name):
        return False
    _assign_default_officer(ctx, modal, 0, default_officer)

    if not ui.click_button(ctx, "Thêm đầu việc"):
        ctx.log("Khong bam duoc Them dau viec", "WARN")
        return False
    ctx.page.wait_for_timeout(900)
    if not _fill_task(ctx, modal, 1, section_name):
        return False
    _assign_default_officer(ctx, modal, 1, default_officer)

    ui.shot(ctx, "admin_template_form")
    submit = modal.locator("button:has-text('Lưu'), button:has-text('Tạo')").first
    if not submit.count():
        return False
    submit.click(timeout=8000)
    ctx.page.wait_for_timeout(3500)
    ui.shot(ctx, "admin_template_result")

    body = ctx.page.locator("body").inner_text().lower()
    if "thành công" in body or "thanh cong" in body:
        return True
    try:
        modal.wait_for(state="hidden", timeout=8000)
        return True
    except Exception:
        return "/template" in ctx.page.url


def create_checklist_instance(
    ctx: WorkflowContext,
    template_name: str,
    officer_name: str,
    employee_name: str,
) -> bool:
    ui.goto_checklist_list(ctx)
    create_checklist.open_modal(ctx)
    if not create_checklist.fill_form(
        ctx,
        officer_name=officer_name,
        employee_name=employee_name,
        template_name=template_name,
    ):
        create_checklist.close_modal(ctx)
        return False
    ok, _reason = create_checklist.submit(ctx)
    if not ok:
        create_checklist.close_modal(ctx)
        return False
    ui.goto_checklist_list(ctx)
    return True


def list_shows_checklist(ctx: WorkflowContext, template_name: str) -> bool:
    target = template_name.strip().lower()
    for row in ui.data_table_rows(ctx):
        if target in row.inner_text().lower():
            return True
    return False
