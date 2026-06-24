# -*- coding: utf-8 -*-
"""
BR-TPL-01 — Template Tuyển dụng OFF → không hiện trong dropdown Tạo checklist.
"""
from __future__ import annotations

from playwright.sync_api import Locator

from workflow.common import WorkflowContext

CASE_ID = "BR-TPL-01"
TEMPLATE_NAME = "Tuyển dụng"
TEMPLATE_CODE = "tuyendung"


def _template_row(ctx: WorkflowContext) -> Locator:
    rows = ctx.page.locator("tbody tr")
    for row in rows.all():
        text = row.inner_text()
        if TEMPLATE_NAME in text and TEMPLATE_CODE in text.lower():
            return row
    return ctx.page.locator("tbody tr").filter(has_text=TEMPLATE_NAME).first


def _status_switch(row: Locator) -> Locator:
    return row.locator(".ant-switch").first


def _is_switch_active(row: Locator) -> bool:
    switch = _status_switch(row)
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


def _click_status_switch(ctx: WorkflowContext, row: Locator) -> None:
    switch = _status_switch(row)
    switch.scroll_into_view_if_needed()
    switch.click()
    ctx.page.wait_for_timeout(1500)


def _ensure_template_off(ctx: WorkflowContext) -> None:
    row = _template_row(ctx)
    row.wait_for(state="visible", timeout=10000)

    if not _is_switch_active(row):
        ctx.log(f"Template [{TEMPLATE_NAME}] da Off — bo qua toggle")
        ctx.screenshot("template_already_off")
        return

    ctx.log(f"Template [{TEMPLATE_NAME}] dang Active — auto click chuyen Off")
    ctx.screenshot("template_active_before_off")

    for attempt in range(1, 4):
        _click_status_switch(ctx, row)
        if not _is_switch_active(row):
            ctx.log("Da chuyen Off thanh cong")
            ctx.screenshot("template_off")
            return
        ctx.log(f"Van Active sau click — thu lai lan {attempt}", "WARN")

    raise RuntimeError(f"Khong the chuyen template [{TEMPLATE_NAME}] sang Off")


def _set_template_active(ctx: WorkflowContext, active: bool) -> None:
    row = _template_row(ctx)
    row.wait_for(state="visible", timeout=10000)
    is_on = _is_switch_active(row)

    if is_on != active:
        ctx.log(
            f"Chuyen trang thai: {'Active' if is_on else 'Off'} → {'Active' if active else 'Off'}"
        )
        _click_status_switch(ctx, row)
        if _is_switch_active(row) != active:
            _click_status_switch(ctx, row)

    ctx.screenshot(f"template_{'on' if active else 'off'}")


def _open_create_checklist_modal(ctx: WorkflowContext) -> None:
    btn = ctx.page.get_by_role("button", name="Tạo checklist")
    btn.first.click()
    ctx.page.wait_for_timeout(800)
    ctx.page.locator(".ant-modal").filter(has_text="Tạo checklist").wait_for(timeout=10000)


def _open_template_dropdown(ctx: WorkflowContext) -> list[str]:
    modal = ctx.page.locator(".ant-modal").filter(has_text="Tạo checklist")
    select = modal.locator(".ant-select").first
    select.click()
    ctx.page.wait_for_timeout(600)
    options = ctx.page.locator(".ant-select-item-option-content")
    options.first.wait_for(timeout=8000)
    texts = [t.strip() for t in options.all_text_contents() if t.strip()]
    ctx.screenshot("template_dropdown")
    return texts


def _close_modal(ctx: WorkflowContext) -> None:
    close_btn = ctx.page.locator(".ant-modal").get_by_role("button", name="Đóng")
    if close_btn.count():
        close_btn.first.click()
    else:
        ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(400)


def run(ctx: WorkflowContext) -> dict:
    was_active: bool | None = None
    try:
        ctx.login_admin()

        ctx.goto("/hrm/checklist/template")
        ctx.screenshot("template_list_before")

        row = _template_row(ctx)
        row.wait_for(state="visible", timeout=10000)
        was_active = _is_switch_active(row)
        ctx.log(
            f"Template [{TEMPLATE_NAME}] trang thai ban dau: "
            f"{'Active' if was_active else 'Off'}"
        )

        _ensure_template_off(ctx)
        ctx.log(f"Template [{TEMPLATE_NAME}] san sang test (Off)")

        ctx.goto("/hrm/checklist")
        _open_create_checklist_modal(ctx)
        option_texts = _open_template_dropdown(ctx)
        ctx.log(f"Dropdown Template: {option_texts}")

        has_tuyendung = any(TEMPLATE_NAME in t for t in option_texts)
        _close_modal(ctx)

        if has_tuyendung:
            return {
                "result": "Fail",
                "message": f'"{TEMPLATE_NAME}" van hien trong dropdown khi template Off',
                "options": option_texts,
            }

        return {
            "result": "Pass",
            "message": f'"{TEMPLATE_NAME}" khong hien trong dropdown khi Off — dung BR',
            "options": option_texts,
        }
    finally:
        try:
            ctx.goto("/hrm/checklist/template")
            if was_active is True:
                _set_template_active(ctx, active=True)
                ctx.log(f"Teardown: bat lai Active cho [{TEMPLATE_NAME}]")
        except Exception as exc:  # noqa: BLE001
            ctx.log(f"Teardown loi: {exc}", "WARN")
