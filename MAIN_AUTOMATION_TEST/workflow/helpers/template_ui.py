# -*- coding: utf-8 -*-
"""UI helpers — màn Mẫu checklist template."""
from __future__ import annotations

from playwright.sync_api import Locator

from workflow.common import WorkflowContext
from workflow.helpers.checklist_ui import fail_with_shot, goto_template_list, shot, table_headers
from workflow.helpers.outcome import fail_result, pass_result

TEMPLATE_HEADERS = ["STT", "Mã template", "Tên template", "Mô tả", "Trạng thái", "Ngày tạo", "Chức năng"]

# Tạo template — fill nhanh (tránh type từng ký tự delay=40)
_TEMPLATE_INPUT_PAUSE_MS = 60


def _read_input_value(inp: Locator) -> str:
    try:
        return inp.input_value().strip()
    except Exception:
        return (inp.get_attribute("value") or "").strip()


def fill_input_verified(ctx: WorkflowContext, inp: Locator, value: str, label: str) -> bool:
    """Điền input/textarea trong modal template — fill() trước, verify sau."""
    expected = value.strip()
    inp.scroll_into_view_if_needed()
    inp.click(timeout=8000)
    inp.fill(expected)
    ctx.page.wait_for_timeout(_TEMPLATE_INPUT_PAUSE_MS)
    if _read_input_value(inp) == expected:
        return True
    inp.click()
    inp.fill("")
    ctx.page.wait_for_timeout(40)
    inp.fill(expected)
    ctx.page.wait_for_timeout(_TEMPLATE_INPUT_PAUSE_MS)
    actual = _read_input_value(inp)
    if actual != expected:
        ctx.log(f"{label}: gia tri khong khop — can [{expected}], co [{actual}]", "WARN")
        return False
    return True


def wait_template_modal_saved(ctx: WorkflowContext, modal: Locator) -> None:
    """Chờ modal đóng sau Lưu — nhanh hơn sleep cố định 3.5s."""
    try:
        modal.wait_for(state="hidden", timeout=6000)
    except Exception:
        ctx.page.wait_for_timeout(800)


def template_row(ctx: WorkflowContext, name: str, code: str = "") -> Locator:
    rows = ctx.page.locator("tbody tr")
    for row in rows.all():
        text = row.inner_text()
        if name in text and (not code or code.lower() in text.lower()):
            return row
    return ctx.page.locator("tbody tr").filter(has_text=name).first


def status_switch(row: Locator) -> Locator:
    return row.locator(".ant-switch").first


def is_switch_active(row: Locator) -> bool:
    switch = status_switch(row)
    switch.wait_for(state="visible", timeout=10000)
    checked = switch.get_attribute("aria-checked")
    if checked == "true":
        return True
    if checked == "false":
        return False
    classes = switch.get_attribute("class") or ""
    if "ant-switch-checked" in classes:
        return True
    label = (switch.inner_text() or "").strip()
    if label.lower() == "off":
        return False
    if "Active" in label:
        return True
    return False


def click_status_switch(ctx: WorkflowContext, row: Locator) -> None:
    switch = status_switch(row)
    switch.scroll_into_view_if_needed()
    switch.click()
    ctx.page.wait_for_timeout(1500)


def ensure_template_off(ctx: WorkflowContext, name: str, code: str = "") -> None:
    row = template_row(ctx, name, code)
    row.wait_for(state="visible", timeout=10000)
    if not is_switch_active(row):
        shot(ctx, "template_already_off")
        return
    shot(ctx, "template_active_before_off")
    for attempt in range(1, 4):
        click_status_switch(ctx, row)
        if not is_switch_active(row):
            shot(ctx, "template_off")
            return
        ctx.log(f"Van Active sau click — thu lai lan {attempt}", "WARN")
    raise RuntimeError(f"Khong the chuyen template [{name}] sang Off")


def set_template_active(ctx: WorkflowContext, name: str, active: bool, code: str = "") -> None:
    row = template_row(ctx, name, code)
    row.wait_for(state="visible", timeout=10000)
    is_on = is_switch_active(row)
    if is_on != active:
        click_status_switch(ctx, row)
        if is_switch_active(row) != active:
            click_status_switch(ctx, row)
    shot(ctx, f"template_{'on' if active else 'off'}")


def assert_template_list_page(ctx: WorkflowContext) -> dict:
    goto_template_list(ctx)
    shot(ctx, "template_list")
    headers = table_headers(ctx)
    has_create = ctx.page.locator("button:has-text('Tạo template mới')").count() > 0
    if not has_create:
        return fail_with_shot(ctx, "Khong thay button [Tao template moi]", "template_list")
    missing = [h for h in TEMPLATE_HEADERS if not any(h in x for x in headers)]
    if missing and headers:
        ctx.log(f"Headers thieu: {missing}", "WARN")
    return pass_result("ADMIN — danh sach template OK", headers=headers)


def open_template_view(ctx: WorkflowContext, name: str = "Tuyển dụng") -> bool:
    row = template_row(ctx, name)
    eye = row.locator("button .anticon-eye, a .anticon-eye, [aria-label='eye']").first
    if eye.count():
        eye.click()
    else:
        row.locator("td").last.locator("button, a").first.click()
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "template_view")
    return True


def open_template_edit(ctx: WorkflowContext, name: str) -> bool:
    row = template_row(ctx, name)
    edit = row.locator("button .anticon-edit, a .anticon-edit").first
    if edit.count():
        edit.click()
    else:
        buttons = row.locator("td").last.locator("button, a")
        if buttons.count() >= 2:
            buttons.nth(1).click()
        else:
            return False
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "template_edit")
    return True
