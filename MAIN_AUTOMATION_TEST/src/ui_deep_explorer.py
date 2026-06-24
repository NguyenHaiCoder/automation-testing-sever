# -*- coding: utf-8 -*-
"""
Deep UI explore: filter, search, create, view, edit, row detail.
Chup anh tung buoc. Khong xac nhan xoa/huy that.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page, TimeoutError as PWTimeout


def _slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^\w\-]+", "_", text, flags=re.UNICODE).strip("_")
    return (s[:max_len] if s else "action")


def shot(page: Page, layout, role: str, page_key: str, action: str) -> str:
    """Luu anh vao picture/{ROLE}/ — ten file khong prefix role."""
    name = f"{page_key}_{_slug(action)}.png"
    path = layout.picture_dir_for_role(role) / name
    page.screenshot(path=str(path), full_page=True)
    return f"{role}/{name}"


def dismiss_overlay(page: Page):
    for sel in [
        "button:has-text('Hủy')",
        "button:has-text('Đóng')",
        "button:has-text('Cancel')",
        "button:has-text('Không')",
        ".ant-modal-close",
        "[aria-label='Close']",
    ]:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                loc.click(timeout=2000)
                page.wait_for_timeout(800)
                return
        except Exception:
            continue
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except Exception:
        pass


def extract_filters(page: Page) -> list[dict]:
    return page.evaluate(
        """() => {
        const out = [];
        const add = (el, kind) => {
            const ph = el.placeholder || el.getAttribute('aria-label') || '';
            const val = el.value || el.innerText || '';
            const rect = el.getBoundingClientRect();
            const visible = rect.width > 0 && rect.height > 0;
            out.push({
                kind,
                tag: el.tagName.toLowerCase(),
                placeholder: ph.slice(0, 80),
                value: (val + '').slice(0, 80),
                visible,
                disabled: !!el.disabled,
                className: (el.className || '').toString().slice(0, 60),
            });
        };
        document.querySelectorAll('input[type="text"], input:not([type]), textarea').forEach(el => {
            if (el.closest('.ant-pagination')) return;
            add(el, 'input');
        });
        document.querySelectorAll('.ant-select, .ant-picker, select').forEach(el => {
            const t = (el.innerText || '').trim().slice(0, 80);
            const rect = el.getBoundingClientRect();
            out.push({
                kind: el.classList.contains('ant-picker') ? 'date_picker' : 'select',
                tag: el.tagName.toLowerCase(),
                text: t,
                visible: rect.width > 0 && rect.height > 0,
                className: (el.className || '').toString().slice(0, 60),
            });
        });
        return out;
    }"""
    )


def record_action(actions: list, **kwargs):
    actions.append(kwargs)


def safe_click(page: Page, locator, log, label: str) -> bool:
    try:
        if locator.count() == 0:
            log.log(f"    skip {label}: not found", "WARN")
            return False
        loc = locator.first
        if not loc.is_visible():
            log.log(f"    skip {label}: hidden", "WARN")
            return False
        loc.scroll_into_view_if_needed(timeout=5000)
        loc.click(timeout=8000)
        page.wait_for_timeout(1500)
        log.log(f"    clicked: {label}")
        return True
    except Exception as e:
        log.log(f"    fail {label}: {str(e)[:100]}", "WARN")
        return False


def probe_element(page: Page, locator, label: str) -> dict[str, Any]:
    """Kiem tra phan tu co ton tai / visible / click duoc khong."""
    info: dict[str, Any] = {"label": label, "found": False, "clickable": False}
    try:
        if locator.count() == 0:
            info["reason"] = "not_found"
            return info
        el = locator.first
        info["found"] = True
        info["visible"] = el.is_visible()
        try:
            info["disabled"] = el.is_disabled()
        except Exception:
            info["disabled"] = False
        info["clickable"] = info["visible"] and not info.get("disabled", False)
        if info["clickable"]:
            info["clickable"] = el.evaluate(
                """el => {
                const s = window.getComputedStyle(el);
                return s.pointerEvents !== 'none' && s.cursor !== 'not-allowed';
            }"""
            )
        info["reason"] = "ok" if info.get("clickable") else "not_clickable"
        return info
    except Exception as e:
        info["reason"] = str(e)[:80]
        return info


def extract_status_switches(page: Page) -> list[dict]:
    return page.evaluate(
        """() => {
        const rows = Array.from(document.querySelectorAll('tbody tr.ant-table-row'))
            .filter(tr => !tr.classList.contains('ant-table-measure-row'));
        return rows.map((row, ri) => {
            const sw = row.querySelector('.ant-switch');
            if (!sw) return null;
            const rect = sw.getBoundingClientRect();
            const style = window.getComputedStyle(sw);
            const checked = sw.getAttribute('aria-checked') === 'true'
                || sw.classList.contains('ant-switch-checked');
            return {
                rowIndex: ri,
                checked,
                text: (sw.innerText || '').trim(),
                visible: rect.width > 0 && rect.height > 0,
                disabled: sw.classList.contains('ant-switch-disabled')
                    || sw.getAttribute('aria-disabled') === 'true',
                pointerEvents: style.pointerEvents,
                className: (sw.className || '').toString().slice(0, 80),
            };
        }).filter(Boolean);
    }"""
    )


def extract_function_buttons(page: Page) -> list[dict]:
    """3 nut Chuc nang (xem / sua / xoa) moi dong."""
    return page.evaluate(
        """() => {
        const rows = Array.from(document.querySelectorAll('tbody tr.ant-table-row'))
            .filter(tr => !tr.classList.contains('ant-table-measure-row'));
        return rows.map((row, ri) => {
            const lastTd = row.querySelector('td:last-child');
            if (!lastTd) return { rowIndex: ri, buttons: [] };
            const btns = Array.from(lastTd.querySelectorAll(
                'button, a.ant-btn, [role="button"], span.anticon, .ant-btn'
            )).filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            });
            return {
                rowIndex: ri,
                buttons: btns.map((b, bi) => {
                    const style = window.getComputedStyle(b);
                    return {
                        index: bi,
                        tag: b.tagName.toLowerCase(),
                        className: (b.className || '').toString().slice(0, 80),
                        ariaLabel: b.getAttribute('aria-label') || '',
                        visible: true,
                        disabled: !!b.disabled || b.getAttribute('aria-disabled') === 'true',
                        pointerEvents: style.pointerEvents,
                        hasInfo: !!b.querySelector('.anticon-info-circle, .anticon-eye'),
                        hasEdit: !!b.querySelector('.anticon-edit, .anticon-form'),
                        hasDelete: !!b.querySelector('.anticon-delete, .anticon-trash'),
                    };
                }),
            };
        });
    }"""
    )


def click_with_strategies(
    page: Page,
    row,
    selectors: list[str],
    log,
    label: str,
) -> bool:
    for sel in selectors:
        loc = row.locator(sel)
        if loc.count() == 0:
            continue
        prob = probe_element(page, loc, f"{label}:{sel}")
        if prob.get("found") and safe_click(page, loc, log, f"{label} ({sel})"):
            return True
    return False


def explore_status_toggles(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
):
    """Toggle Trang thai (Active/Inactive) — dong dau bang."""
    switches = extract_status_switches(page)
    log.log(f"  status switches found: {len(switches)}")
    if not switches:
        record_action(actions, action="status_toggle", success=False, found=False, note="no ant-switch in table")
        return

    sw0 = switches[0]
    record_action(actions, action="status_toggle_probe", **sw0)

    row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first
    toggle = row.locator(".ant-switch").first
    prob = probe_element(page, toggle, "status_toggle")

    before_checked = sw0.get("checked")
    shot(page, layout, role, page_key, "status_toggle_before")

    clicked = safe_click(page, toggle, log, "status_toggle")
    if not clicked:
        try:
            toggle.click(force=True, timeout=5000)
            page.wait_for_timeout(1000)
            clicked = True
            log.log("    force-clicked: status_toggle", "WARN")
        except Exception:
            pass
    after = extract_status_switches(page)
    after_checked = after[0].get("checked") if after else None
    changed = before_checked != after_checked

    record_action(
        actions,
        action="status_toggle_click",
        success=clicked,
        clickable=prob.get("clickable", False),
        before_checked=before_checked,
        after_checked=after_checked,
        state_changed=changed,
        screenshot=shot(page, layout, role, page_key, "status_toggle_after"),
        note="BUG: khong doi trang thai" if clicked and not changed else "",
    )

    # Toggle lai neu da doi (tranh doi data test)
    if changed and clicked:
        safe_click(page, toggle, log, "status_toggle_revert")
        page.wait_for_timeout(800)


def explore_function_column(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
):
    """3 nut Chuc nang: xem (i) / sua (but) / xoa (thung rac)."""
    fn_buttons = extract_function_buttons(page)
    log.log(f"  function column rows: {len(fn_buttons)}")
    record_action(actions, action="function_buttons_scan", rows=fn_buttons)

    row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first
    if row.count() == 0:
        record_action(actions, action="function_buttons", success=False, found=False)
        return

    action_cell = row.locator("td").last
    before_url = page.url

    action_defs = [
        (
            "action_view",
            [
                "button:has(.anticon-info-circle)",
                "button:has(.anticon-eye)",
                ".anticon-info-circle",
                "td:last-child button:nth-child(1)",
                "td:last-child a:nth-child(1)",
                "td:last-child span.anticon-info-circle",
            ],
        ),
        (
            "action_edit",
            [
                "button:has(.anticon-edit)",
                "button:has(.anticon-form)",
                ".anticon-edit",
                "td:last-child button:nth-child(2)",
                "td:last-child span.anticon-edit",
            ],
        ),
        (
            "action_delete",
            [
                "button:has(.anticon-delete)",
                "button:has(.anticon-trash)",
                ".anticon-delete",
                "td:last-child button:nth-child(3)",
                "td:last-child span.anticon-delete",
            ],
        ),
    ]

    for action_name, selectors in action_defs:
        prob = probe_element(page, action_cell.locator(selectors[0]), action_name)
        clicked = click_with_strategies(page, row, selectors, log, action_name)
        if not clicked:
            try:
                loc = row.locator(selectors[0]).first
                if loc.count() > 0:
                    loc.click(force=True, timeout=5000)
                    page.wait_for_timeout(1000)
                    clicked = True
                    log.log(f"    force-clicked: {action_name}", "WARN")
            except Exception:
                pass
        record_action(
            actions,
            action=f"{action_name}_click",
            success=clicked,
            clickable=prob.get("clickable", False),
            probe=prob,
            screenshot=shot(page, layout, role, page_key, action_name),
            url=page.url,
            modal_open=page.locator(".ant-modal, .ant-drawer, .ant-popconfirm").count() > 0,
            note="BUG: khong bam duoc" if not clicked else "",
        )
        dismiss_overlay(page)
        if page.url != before_url:
            page.goto(before_url, wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first


def explore_date_range_calendar(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
):
    """Calendar range: mo → luot thang → chon start/end → search."""
    picker = page.locator(".ant-picker-range").first
    if picker.count() == 0:
        picker = page.locator(".ant-picker").first
    if picker.count() == 0:
        record_action(actions, action="calendar", success=False, found=False)
        return

    if not safe_click(page, picker, log, "calendar_open"):
        record_action(actions, action="calendar_open", success=False)
        return

    dropdown = page.locator(".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)")
    try:
        dropdown.first.wait_for(state="visible", timeout=8000)
    except PWTimeout:
        record_action(actions, action="calendar_open", success=False, note="dropdown khong hien")
        return

    record_action(
        actions,
        action="calendar_open",
        screenshot=shot(page, layout, role, page_key, "calendar_open"),
    )

    # Luot thang — next / prev
    for nav_sel, nav_name in [
        (".ant-picker-dropdown .ant-picker-header-next-btn", "calendar_next_month"),
        (".ant-picker-dropdown .ant-picker-header-prev-btn", "calendar_prev_month"),
    ]:
        if safe_click(page, page.locator(nav_sel), log, nav_name):
            record_action(
                actions,
                action=nav_name,
                screenshot=shot(page, layout, role, page_key, nav_name),
            )

    # Chon ngay start + end (2 click tren o in-view)
    cells = page.locator(
        ".ant-picker-dropdown .ant-picker-cell-in-view:not(.ant-picker-cell-disabled) .ant-picker-cell-inner"
    )
    cell_count = cells.count()
    log.log(f"  calendar cells selectable: {cell_count}")
    if cell_count >= 2:
        try:
            start_idx = 0
            end_idx = min(7, cell_count - 1)
            cells.nth(start_idx).click(timeout=5000)
            page.wait_for_timeout(600)
            record_action(
                actions,
                action="calendar_pick_start",
                cell_index=start_idx,
                screenshot=shot(page, layout, role, page_key, "calendar_pick_start"),
            )
            cells.nth(end_idx).click(timeout=5000)
            page.wait_for_timeout(800)
            record_action(
                actions,
                action="calendar_pick_end",
                cell_index=end_idx,
                screenshot=shot(page, layout, role, page_key, "calendar_range_selected"),
            )
        except Exception as e:
            record_action(actions, action="calendar_pick", success=False, error=str(e)[:120])
    else:
        record_action(actions, action="calendar_pick", success=False, note=f"cells={cell_count}")

    # Doc gia tri input sau khi chon
    try:
        inputs = page.locator(".ant-picker-range input, .ant-picker input").all()
        values = [inp.input_value() for inp in inputs[:2] if inp.is_visible()]
        record_action(actions, action="calendar_values", values=values)
        log.log(f"  calendar values: {values}")
    except Exception:
        pass

    # Dong calendar (click ngoai hoac Escape) roi search
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except Exception:
        pass

    safe_click(page, page.locator("button .anticon-search, button:has(.anticon-search)"), log, "calendar_search")
    page.wait_for_timeout(1500)
    record_action(
        actions,
        action="calendar_search_submit",
        screenshot=shot(page, layout, role, page_key, "calendar_search_result"),
        url=page.url,
    )


def extract_journal_buttons(page: Page) -> list[dict]:
    """Tim nut Nhat ky dong — khong hardcode so (1)."""
    return page.evaluate(
        """() => {
        return Array.from(document.querySelectorAll('button, a.ant-btn, [role="button"]'))
            .filter(el => /Nhật ký|Nhat ky/i.test((el.innerText || '').trim()))
            .map((el, i) => {
                const r = el.getBoundingClientRect();
                return {
                    index: i,
                    text: (el.innerText || '').trim().slice(0, 80),
                    visible: r.width > 0 && r.height > 0,
                    disabled: !!el.disabled,
                    className: (el.className || '').toString().slice(0, 60),
                };
            });
    }"""
    )


def explore_checklist_detail_page(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
):
    """Man chi tiet: Nhat ky (dynamic), Huy checklist, Quay lai."""
    journals = extract_journal_buttons(page)
    log.log(f"  detail journals found: {len(journals)}")
    record_action(actions, action="journal_scan", buttons=journals)

    # --- Nhat ky — bam tung nut tim duoc (text dong, vd "Nhật ký (1)") ---
    journal_loc = page.locator("button, a.ant-btn").filter(has_text=re.compile(r"Nhật ký|Nhat ky", re.I))
    jcount = journal_loc.count()
    for i in range(min(jcount, 5)):
        btn = journal_loc.nth(i)
        try:
            label = btn.inner_text().strip()
        except Exception:
            label = f"journal_{i}"
        slug = _slug(label) or f"journal_{i}"
        if safe_click(page, btn, log, f"journal_{slug}"):
            expanded = page.locator(
                ".ant-collapse-item-active, .ant-dropdown-open, .ant-timeline, .ant-drawer-open"
            ).count() > 0
            record_action(
                actions,
                action="journal_click",
                index=i,
                label=label,
                screenshot=shot(page, layout, role, page_key, f"journal_{slug}"),
                expanded=expanded,
            )
            dismiss_overlay(page)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
        else:
            record_action(actions, action="journal_click", index=i, label=label, success=False)

    # --- Huy checklist (chi mo dialog, khong xac nhan huy that) ---
    cancel_btn = page.locator("button:has-text('Hủy checklist'), button:has-text('Huy checklist')")
    prob_cancel = probe_element(page, cancel_btn, "cancel_checklist")
    if safe_click(page, cancel_btn, log, "cancel_checklist"):
        record_action(
            actions,
            action="cancel_checklist_click",
            probe=prob_cancel,
            screenshot=shot(page, layout, role, page_key, "cancel_checklist_modal"),
            modal_open=page.locator(".ant-modal, .ant-popconfirm").count() > 0,
            role_allowed=role == "ADMIN",
            note="BUG: EMPLOYEE/OFFICER thay nut Huy?" if role != "ADMIN" else "",
        )
        dismiss_overlay(page)
    else:
        record_action(
            actions,
            action="cancel_checklist_click",
            success=False,
            probe=prob_cancel,
            note="BUG: khong bam duoc Huy checklist",
        )

    # --- Quay lai (cuoi cung — co the navigate ra list) ---
    back_btn = page.locator("button:has-text('Quay lại'), button:has-text('Quay lai')")
    if safe_click(page, back_btn, log, "quay_lai"):
        record_action(
            actions,
            action="quay_lai_click",
            screenshot=shot(page, layout, role, page_key, "after_quay_lai"),
            url=page.url,
        )


def explore_toolbar_filters(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
) -> list[dict]:
    """Tim kiem + filter + refresh tren list checklist."""
    filters = extract_filters(page)
    log.log(f"  filters/inputs found: {len(filters)}")

    # o tim kiem
    search = page.locator(
        'input[placeholder*="checklist" i], input[placeholder*="Tên" i], '
        'input[placeholder*="nhân" i], input[placeholder*="nhan" i]'
    ).first
    if search.count() > 0:
        try:
            search.fill("test")
            page.wait_for_timeout(500)
            record_action(actions, action="search_fill", value="test", screenshot=shot(page, layout, role, page_key, "search_filled"))
            # nut tim (kinh lup)
            safe_click(page, page.locator("button .anticon-search, button:has(.anticon-search)"), log, "search_button")
            record_action(
                actions,
                action="search_submit",
                screenshot=shot(page, layout, role, page_key, "search_result"),
                url=page.url,
            )
        except Exception as e:
            record_action(actions, action="search_fill", success=False, error=str(e)[:120])

    # date range calendar — mo, luot thang, chon ngay start/end
    explore_date_range_calendar(page, layout, role, page_key, log, actions)

    # dropdown Tat ca / Trang thai
    for i, sel in enumerate(page.locator(".ant-select:not(.ant-pagination-options-size-changer)").all()[:3]):
        try:
            if not sel.is_visible():
                continue
            sel.click(timeout=5000)
            page.wait_for_timeout(1000)
            record_action(
                actions,
                action=f"dropdown_open_{i}",
                screenshot=shot(page, layout, role, page_key, f"dropdown_{i}"),
            )
            dismiss_overlay(page)
            page.keyboard.press("Escape")
            page.wait_for_timeout(400)
        except Exception as e:
            record_action(actions, action=f"dropdown_open_{i}", success=False, error=str(e)[:80])

    # nut refresh
    if safe_click(page, page.locator("button .anticon-reload, button:has(.anticon-sync)"), log, "refresh"):
        page.wait_for_timeout(1500)
        record_action(actions, action="refresh", screenshot=shot(page, layout, role, page_key, "after_refresh"), url=page.url)

    return filters


def explore_primary_buttons(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
    button_texts: list[str],
):
    for text in button_texts:
        loc = page.locator(f"button:has-text('{text}')")
        if not safe_click(page, loc, log, text):
            record_action(actions, action=f"button_{_slug(text)}", success=False, found=False)
            continue
        record_action(
            actions,
            action=f"button_{_slug(text)}",
            label=text,
            screenshot=shot(page, layout, role, page_key, f"btn_{_slug(text)}"),
            url=page.url,
            modal_open=page.locator(".ant-modal, .ant-drawer").count() > 0,
        )
        dismiss_overlay(page)
        page.wait_for_timeout(800)


def explore_table_row_actions(
    page: Page,
    layout,
    role: str,
    page_key: str,
    log,
    actions: list,
    allow_delete_dialog: bool = True,
) -> dict | None:
    """Click xem detail (row / icon info), edit, delete (chi chup dialog roi huy)."""
    row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first
    if row.count() == 0:
        log.log("  no table rows for actions", "WARN")
        return None

    detail_url = None
    cells = row.locator("td")
    action_cell = row.locator("td").last

    # --- row click -> detail ---
    before = page.url
    if safe_click(page, row, log, "row_open_detail"):
        if page.url != before:
            detail_url = page.url
            record_action(
                actions,
                action="row_detail",
                screenshot=shot(page, layout, role, page_key, "row_detail"),
                url=page.url,
            )
            page.go_back(wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
        else:
            dismiss_overlay(page)

    # --- icon Chuc nang (fallback cho checklist list) ---
    icon_map = [
        ("button:has(.anticon-info-circle), .anticon-info-circle", "action_view"),
        ("button:has(.anticon-edit), .anticon-edit", "action_edit"),
        ("button:has(.anticon-delete), .anticon-delete", "action_delete"),
    ]
    for selector, action_name in icon_map:
        if not click_with_strategies(page, row, [selector], log, action_name):
            record_action(actions, action=action_name, success=False, found=False)
            continue
        record_action(
            actions,
            action=action_name,
            screenshot=shot(page, layout, role, page_key, action_name),
            url=page.url,
            confirm_dialog=page.locator(".ant-modal-confirm, .ant-popconfirm").count() > 0,
        )
        dismiss_overlay(page)
        if page.url != before and "/hrm/checklist" in page.url:
            page.go_back(wait_until="domcontentloaded")
            page.wait_for_timeout(1200)

    return {"detail_url": detail_url}


def deep_explore_page(
    page: Page,
    layout,
    role: str,
    page_key: str,
    page_name: str,
    base_url: str,
    log,
) -> dict[str, Any]:
    """Explore day du 1 man sau khi da navigate."""
    from src.page_explorer import extract_buttons, extract_tables

    result: dict[str, Any] = {
        "page_name": page_name,
        "url": page.url,
        "screenshot_baseline": shot(page, layout, role, page_key, "baseline"),
        "tables": extract_tables(page),
        "buttons": extract_buttons(page),
        "filters": extract_filters(page),
        "interactions": [],
    }

    log.log(f"  deep explore: {page_name}")

    if page_key == "hrm_checklist_template":
        explore_primary_buttons(
            page, layout, role, page_key, log, result["interactions"],
            ["Tạo template mới", "Thêm", "Tạo mới"],
        )
        explore_toolbar_filters(page, layout, role, page_key, log, result["interactions"])
        result["status_switches"] = extract_status_switches(page)
        result["function_buttons"] = extract_function_buttons(page)
        explore_status_toggles(page, layout, role, page_key, log, result["interactions"])
        explore_function_column(page, layout, role, page_key, log, result["interactions"])
        explore_table_row_actions(page, layout, role, page_key, log, result["interactions"])

    elif page_key == "hrm_checklist":
        create_btns = ["Tạo checklist", "+ Tạo checklist"] if role == "ADMIN" else []
        explore_primary_buttons(page, layout, role, page_key, log, result["interactions"], create_btns)
        explore_toolbar_filters(page, layout, role, page_key, log, result["interactions"])
        detail = explore_table_row_actions(page, layout, role, page_key, log, result["interactions"])
        if detail and detail.get("detail_url"):
            result["detail_url_from_row"] = detail["detail_url"]

    else:
        # Chi tiet checklist instance
        explore_checklist_detail_page(page, layout, role, page_key, log, result["interactions"])
        explore_primary_buttons(
            page, layout, role, page_key, log, result["interactions"],
            ["Xác nhận", "Đổi cán bộ"],
        )
        result["journals"] = extract_journal_buttons(page)
        result["screenshot_detail"] = shot(page, layout, role, page_key, "detail_view")

    result["filters"] = extract_filters(page)
    result["interaction_count"] = len(result["interactions"])
    result["success_clicks"] = sum(1 for a in result["interactions"] if a.get("success", True) is not False)
    return result


def path_to_key(path: str) -> str:
    if "/template" in path:
        return "hrm_checklist_template"
    if path.rstrip("/").endswith("/hrm/checklist"):
        return "hrm_checklist"
    if "/hrm/checklist/" in path:
        return "hrm_checklist_detail"
    return _slug(path)
