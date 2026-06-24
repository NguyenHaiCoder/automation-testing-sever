# -*- coding: utf-8 -*-
"""Modal Tạo checklist — dùng chung ADM-INS-01 / ADM-INS-03."""
from __future__ import annotations

import random
from datetime import date

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui


def open_modal(ctx: WorkflowContext) -> None:
    ui.click_button(ctx, "Tạo checklist")
    ctx.page.locator(".ant-modal").filter(has_text="Tạo checklist").wait_for(timeout=10000)
    ui.shot(ctx, "create_checklist_modal")


def close_modal(ctx: WorkflowContext) -> None:
    close_btn = ctx.page.locator(".ant-modal").get_by_role("button", name="Đóng")
    if close_btn.count():
        close_btn.first.click()
    else:
        ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(400)


def _modal(ctx: WorkflowContext):
    return ctx.page.locator(".ant-modal").filter(has_text="Tạo checklist")


def _click_option(ctx: WorkflowContext, option_text: str) -> bool:
    opt = ctx.page.locator(".ant-select-item-option-content").filter(has_text=option_text).first
    if not opt.count():
        opt = ctx.page.get_by_text(option_text, exact=True)
    if not opt.count():
        return False
    opt.click(timeout=8000)
    ctx.page.wait_for_timeout(1000)
    return True


def _select_by_label(ctx: WorkflowContext, modal, label_part: str, option_text: str) -> bool:
    for item in modal.locator(".ant-form-item").all():
        try:
            label_el = item.locator(".ant-form-item-label, label").first
            if not label_el.count():
                continue
            if label_part.lower() not in label_el.inner_text().lower():
                continue
            sel = item.locator(".ant-select").first
            if not sel.count():
                continue
            sel.click(timeout=8000)
            ctx.page.wait_for_timeout(500)
            inp = sel.locator("input").first
            if inp.count():
                inp.fill(option_text)
                ctx.page.wait_for_timeout(700)
            if _click_option(ctx, option_text):
                return True
        except Exception:
            continue
    return False


def _select_nth(ctx: WorkflowContext, modal, index: int, option_text: str) -> bool:
    sel = modal.locator(".ant-select").nth(index)
    if not sel.count():
        return False
    sel.click(timeout=8000)
    ctx.page.wait_for_timeout(500)
    inp = sel.locator("input").first
    if inp.count():
        inp.fill(option_text)
        ctx.page.wait_for_timeout(700)
    return _click_option(ctx, option_text)


def _dismiss_layers(ctx: WorkflowContext, modal) -> None:
    try:
        if ctx.page.locator(".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)").count():
            modal.locator(".ant-modal-header, .ant-modal-title").first.click(timeout=3000)
            ctx.page.wait_for_timeout(300)
    except Exception:
        pass
    try:
        if ctx.page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").count():
            modal.locator(".ant-modal-body").first.click(timeout=3000)
            ctx.page.wait_for_timeout(200)
    except Exception:
        pass


def _template_select(modal):
    if modal.locator(".ant-form-item-label").filter(has_text="Template").count():
        item = modal.locator(".ant-form-item").filter(has_text="Template").first
        return item.locator(".ant-select").first
    return modal.locator(".ant-select").first


def _select_template_by_name(ctx: WorkflowContext, modal, template_name: str) -> bool:
    sel = _template_select(modal)
    if not sel.count():
        return False
    target = template_name.strip().lower()
    sel.click(timeout=8000)
    ctx.page.wait_for_timeout(600)
    options = [
        o
        for o in ctx.page.locator(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content"
        ).all()
        if o.inner_text().strip()
    ]
    if not options:
        _dismiss_layers(ctx, modal)
        return _select_by_label(ctx, modal, "Template", template_name)
    for opt in options:
        if opt.inner_text().strip().lower() == target:
            opt.click(timeout=8000)
            ctx.page.wait_for_timeout(800)
            _dismiss_layers(ctx, modal)
            return modal.is_visible()
    candidates: list[tuple[int, object]] = []
    for opt in options:
        text = opt.inner_text().strip()
        tl = text.lower()
        if target in tl or tl in target:
            candidates.append((len(text), opt))
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        candidates[0][1].click(timeout=8000)
        ctx.page.wait_for_timeout(800)
        _dismiss_layers(ctx, modal)
        return modal.is_visible()
    _dismiss_layers(ctx, modal)
    return _select_by_label(ctx, modal, "Template", template_name)


def _select_random_template(ctx: WorkflowContext, modal) -> bool:
    sel = _template_select(modal)
    sel.click(timeout=8000)
    ctx.page.wait_for_timeout(600)
    options = ctx.page.locator(
        ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content"
    ).all()
    if not options:
        options = [o for o in ctx.page.locator(".ant-select-item-option-content").all() if o.is_visible()]
    usable = [o for o in options if o.inner_text().strip()]
    if not usable:
        return False
    random.choice(usable).click(timeout=8000)
    ctx.page.wait_for_timeout(800)
    _dismiss_layers(ctx, modal)
    return modal.is_visible()


def _fill_start_date_today(ctx: WorkflowContext, modal) -> bool:
    today = date.today()
    date_str = today.strftime("%d/%m/%Y")
    picker = modal.locator(".ant-form-item").filter(has_text="Ngày bắt đầu").locator(".ant-picker").first
    if not picker.count():
        picker = modal.locator(".ant-picker").first
    if not picker.count():
        return False
    picker.click(timeout=8000)
    ctx.page.wait_for_timeout(600)
    inp = picker.locator("input").first
    if inp.count():
        inp.click()
        inp.fill(date_str)
        inp.press("Tab")
        ctx.page.wait_for_timeout(600)
        _dismiss_layers(ctx, modal)
        return True
    today_cell = ctx.page.locator(
        ".ant-picker-dropdown:not(.ant-picker-dropdown-hidden) .ant-picker-cell-today"
    ).first
    if today_cell.count():
        today_cell.locator(".ant-picker-cell-inner").click(timeout=5000)
        ctx.page.wait_for_timeout(500)
        _dismiss_layers(ctx, modal)
        return True
    day_cell = ctx.page.locator(
        f".ant-picker-dropdown:not(.ant-picker-dropdown-hidden) "
        f".ant-picker-cell-in-view .ant-picker-cell-inner"
    ).filter(has_text=str(today.day)).first
    if day_cell.count():
        day_cell.click(timeout=5000)
        ctx.page.wait_for_timeout(500)
        _dismiss_layers(ctx, modal)
        return True
    return False


def fill_form(
    ctx: WorkflowContext,
    *,
    officer_name: str,
    employee_name: str,
    template_name: str | None = None,
) -> bool:
    modal = _modal(ctx)
    if modal.locator(".ant-select").count() < 3:
        return False
    if template_name:
        if not _select_template_by_name(ctx, modal, template_name):
            return False
    elif not _select_random_template(ctx, modal):
        return False
    if not _fill_start_date_today(ctx, modal):
        return False
    _dismiss_layers(ctx, modal)
    officer_ok = _select_by_label(ctx, modal, "Cán bộ", officer_name) or _select_by_label(
        ctx, modal, "phụ trách", officer_name
    )
    if not officer_ok:
        officer_ok = _select_nth(ctx, modal, 1, officer_name)
    if not officer_ok:
        return False
    employee_ok = _select_by_label(ctx, modal, "Nhân viên", employee_name)
    if not employee_ok:
        employee_ok = _select_nth(ctx, modal, modal.locator(".ant-select").count() - 1, employee_name)
    if not employee_ok:
        return False
    ui.shot(ctx, "create_filled")
    return True


def _duplicate_in_ui(ctx: WorkflowContext, modal=None) -> bool:
    dup_words = ("trùng", "duplicate", "đã tồn tại", "da ton tai", "ton tai", "đã có", "da co")
    chunks = [ctx.page.locator("body").inner_text().lower()]
    if modal is not None and modal.count():
        chunks.append(modal.inner_text().lower())
    for sel in (".ant-message-notice", ".ant-notification-notice", ".ant-form-item-explain-error"):
        for text in ctx.page.locator(sel).all_inner_texts():
            chunks.append(text.lower())
    combined = " ".join(chunks)
    return any(w in combined for w in dup_words)


def submit(ctx: WorkflowContext) -> tuple[bool, str]:
    modal = _modal(ctx)
    btn = modal.locator("button:has-text('Tạo'), button:has-text('Lưu')").first
    if not btn.count():
        return False, "no_submit_button"
    btn.click(timeout=8000)
    ctx.page.wait_for_timeout(3000)
    ui.shot(ctx, "create_result")
    if _duplicate_in_ui(ctx, modal):
        return False, "duplicate"
    body = ctx.page.locator("body").inner_text().lower()
    if "thành công" in body or "thanh cong" in body:
        return True, "success"
    try:
        modal.wait_for(state="hidden", timeout=8000)
        return True, "modal_closed"
    except Exception:
        return False, "submit_unknown"
