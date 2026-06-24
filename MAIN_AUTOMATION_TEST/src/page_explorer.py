# -*- coding: utf-8 -*-
"""
Explore UI: tables, buttons, links trên các màn Checklist.
Không thực hiện thao tác phá hủy (xóa/hủy/submit form).
"""
from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page, TimeoutError as PWTimeout

DESTRUCTIVE_KEYWORDS = re.compile(
    r"xóa|hủy|delete|remove|cancel|xác nhận hủy|đăng xuất|logout",
    re.I,
)


def _safe_text(el) -> str:
    try:
        return (el.inner_text() or "").strip()[:120]
    except Exception:
        return ""


def is_clickable(page: Page, selector: str) -> dict[str, Any]:
    """Đánh giá phần tử có thể click được không (không thực sự click)."""
    loc = page.locator(selector).first
    if loc.count() == 0:
        return {"exists": False, "clickable": False, "reason": "not_found"}
    try:
        visible = loc.is_visible()
        disabled = loc.is_disabled() if loc.evaluate("el => el.disabled !== undefined") else False
        aria_disabled = (loc.get_attribute("aria-disabled") or "").lower() == "true"
        box = loc.bounding_box()
        in_viewport = box is not None and box.get("width", 0) > 0
        pointer_ok = loc.evaluate(
            """el => {
                const s = window.getComputedStyle(el);
                return s.pointerEvents !== 'none' && s.visibility !== 'hidden' && s.display !== 'none';
            }"""
        )
        clickable = visible and in_viewport and pointer_ok and not disabled and not aria_disabled
        reason = []
        if not visible:
            reason.append("hidden")
        if disabled:
            reason.append("disabled")
        if aria_disabled:
            reason.append("aria-disabled")
        if not pointer_ok:
            reason.append("pointer-events/visibility")
        if not in_viewport:
            reason.append("no_bbox")
        return {
            "exists": True,
            "clickable": clickable,
            "visible": visible,
            "disabled": disabled or aria_disabled,
            "reason": ", ".join(reason) if reason else "ok",
        }
    except Exception as e:
        return {"exists": True, "clickable": False, "reason": str(e)[:100]}


def extract_tables(page: Page) -> list[dict]:
    return page.evaluate(
        """() => {
        const tables = [];
        document.querySelectorAll('.ant-table, table').forEach((tbl, idx) => {
            const headers = Array.from(tbl.querySelectorAll('thead th, thead .ant-table-cell'))
                .map(th => (th.innerText || '').trim()).filter(Boolean);
            const rows = Array.from(tbl.querySelectorAll('tbody tr'))
                .filter(tr => !tr.classList.contains('ant-table-measure-row')
                    && tr.getAttribute('aria-hidden') !== 'true'
                    && (tr.innerText || '').trim().length > 0);
            const empty = !!tbl.closest('.ant-table-wrapper')?.querySelector('.ant-empty')
                || !!document.querySelector('.ant-empty-description');
            const pagination = document.querySelector('.ant-pagination-total-text');
            tables.push({
                index: idx,
                headers,
                rowCount: rows.length,
                empty,
                paginationText: pagination ? pagination.innerText.trim() : null,
                sampleRow: rows[0] ? rows[0].innerText.trim().slice(0, 200) : null,
            });
        });
        return tables;
    }"""
    )


def extract_buttons(page: Page) -> list[dict]:
    items = page.evaluate(
        """() => {
        const out = [];
        const seen = new Set();
        document.querySelectorAll('button, [role="button"], a.ant-btn, .ant-btn').forEach((el, i) => {
            const text = (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 100);
            const key = text + '|' + el.tagName;
            if (!text || seen.has(key)) return;
            seen.add(key);
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            const disabled = el.disabled || el.getAttribute('aria-disabled') === 'true';
            const visible = rect.width > 0 && rect.height > 0
                && style.visibility !== 'hidden' && style.display !== 'none';
            const clickable = visible && !disabled
                && style.pointerEvents !== 'none';
            out.push({
                index: i,
                tag: el.tagName.toLowerCase(),
                text,
                type: el.getAttribute('type'),
                disabled,
                visible,
                clickable,
                className: (el.className || '').toString().slice(0, 80),
            });
        });
        return out;
    }"""
    )
    for item in items:
        item["category"] = (
            "destructive_skip"
            if DESTRUCTIVE_KEYWORDS.search(item.get("text", ""))
            else ("clickable" if item.get("clickable") else "not_clickable")
        )
    return items


def extract_checklist_links(page: Page, base_url: str) -> list[dict]:
    return page.evaluate(
        """(base) => {
        const links = [];
        const seen = new Set();
        document.querySelectorAll('a[href]').forEach(a => {
            const href = a.getAttribute('href') || '';
            if (!href.includes('/hrm/checklist')) return;
            const full = href.startsWith('http') ? href : base + href;
            if (seen.has(full)) return;
            seen.add(full);
            links.push({
                text: (a.innerText || '').trim().slice(0, 80),
                href: full,
                visible: a.offsetParent !== null,
            });
        });
        return links;
    }""",
        base_url,
    )


def extract_menu_items(page: Page) -> list[dict]:
    return page.evaluate(
        """() => {
        const items = [];
        document.querySelectorAll('.ant-menu-item, .ant-menu-submenu-title, [class*="menu"] a').forEach(el => {
            const t = (el.innerText || '').trim();
            if (!t || t.length > 60) return;
            if (/checklist|mẫu/i.test(t)) {
                items.push({
                    text: t,
                    visible: el.offsetParent !== null,
                });
            }
        });
        return items;
    }"""
    )


def try_open_first_table_row(page: Page, log) -> dict | None:
    """Thử mở chi tiết từ dòng đầu bảng (nếu có)."""
    row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first
    if row.count() == 0:
        return None
    before = page.url
    try:
        row.scroll_into_view_if_needed(timeout=5000)
        row.click(timeout=8000)
        page.wait_for_timeout(2500)
        after = page.url
        if after != before and "/hrm/checklist/" in after:
            log.log(f"  Row click → detail: {after}")
            return {"method": "row_click", "url": after}
    except Exception as e:
        log.log(f"  Row click failed: {str(e)[:120]}", "WARN")
    return None


def explore_page(page: Page, url: str, page_name: str, role: str, base_url: str, log) -> dict:
    log.log(f"[{role}] Explore: {page_name} → {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    try:
        page.wait_for_selector(".ant-spin-spinning", state="hidden", timeout=20000)
    except PWTimeout:
        pass

    body_snippet = ""
    try:
        body_snippet = page.locator("body").inner_text()[:300]
    except Exception:
        pass

    is_404 = "404" in body_snippet or "couldn't find your page" in body_snippet.lower()
    forbidden = any(x in body_snippet.lower() for x in ["không có quyền", "403", "từ chối truy cập"])

    result = {
        "role": role,
        "page_name": page_name,
        "url": page.url,
        "requested_url": url,
        "is_404": is_404,
        "forbidden_hint": forbidden,
        "menu_checklist": extract_menu_items(page),
        "tables": extract_tables(page),
        "buttons": extract_buttons(page),
        "checklist_links": extract_checklist_links(page, base_url),
        "body_snippet": body_snippet,
    }

    log.log(
        f"  tables={len(result['tables'])} "
        f"buttons={len(result['buttons'])} "
        f"clickable={sum(1 for b in result['buttons'] if b.get('category')=='clickable')} "
        f"links={len(result['checklist_links'])}"
    )
    for tbl in result["tables"]:
        log.log(
            f"  TABLE #{tbl['index']}: cols={len(tbl.get('headers',[]))} "
            f"rows={tbl.get('rowCount',0)} empty={tbl.get('empty')}"
        )

    return result


def explore_role(
    account,
    settings,
    run_dir,
    layout,
    shared_log,
    routes_for_role: list[dict],
) -> dict:
    """Chạy trong 1 thread — 1 Chromium riêng cho mỗi role."""
    from playwright.sync_api import sync_playwright

    from src.auth import login
    from src.ui_deep_explorer import deep_explore_page, path_to_key

    role = account.role

    def rlog(msg, level="INFO"):
        shared_log.log(f"[{role}] {msg}", level)

    report: dict[str, Any] = {
        "role": role,
        "email": account.email,
        "note": account.note,
        "login_ok": False,
        "pages": [],
        "deep_explores": [],
        "errors": [],
    }

    with sync_playwright() as p:
        launch_kw = {"headless": settings.headless, "slow_mo": settings.slow_mo}
        if not settings.headless:
            launch_kw["args"] = ["--start-maximized"]
        browser = p.chromium.launch(**launch_kw)
        ctx = browser.new_context(no_viewport=not settings.headless)
        page = ctx.new_page()
        if not settings.headless:
            page.bring_to_front()

        try:
            if not login(page, settings, account, shared_log):
                report["errors"].append("login_failed")
                return report
            report["login_ok"] = True

            visited_urls: set[str] = set()

            for route in routes_for_role:
                url = settings.base_url + route["path"]
                if url in visited_urls:
                    continue
                visited_urls.add(url)

                page_key = path_to_key(route["path"])
                page_data = explore_page(
                    page, url, route["name"], role, settings.base_url, shared_log
                )
                report["pages"].append(page_data)

                # Deep explore: search, filter, create, view, edit, row detail + screenshots
                deep = deep_explore_page(
                    page,
                    layout,
                    role,
                    page_key,
                    route["name"],
                    settings.base_url,
                    shared_log,
                )
                report["deep_explores"].append(deep)

                # Mo detail neu row click tra ve URL (checklist list)
                detail_url = deep.get("detail_url_from_row")
                if not detail_url:
                    row_count = sum(t.get("rowCount", 0) for t in page_data.get("tables", []))
                    if route["path"] == "/hrm/checklist" and row_count > 0:
                        det = try_open_first_table_row(page, shared_log)
                        if det:
                            detail_url = det.get("url")

                if detail_url and detail_url not in visited_urls:
                    visited_urls.add(detail_url)
                    page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2000)
                    detail_data = explore_page(
                        page,
                        detail_url,
                        "Chi tiết checklist (instance)",
                        role,
                        settings.base_url,
                        shared_log,
                    )
                    report["pages"].append(detail_data)
                    detail_deep = deep_explore_page(
                        page,
                        layout,
                        role,
                        "hrm_checklist_detail",
                        "Chi tiết checklist",
                        settings.base_url,
                        shared_log,
                    )
                    report["deep_explores"].append(detail_deep)

                rlog(
                    f"Deep done {route['name']}: "
                    f"interactions={deep.get('interaction_count', 0)} "
                    f"screens={deep.get('screenshot_baseline')}"
                )

        except Exception as e:
            report["errors"].append(str(e))
            shared_log.log(f"[{role}] FATAL: {e}", "ERROR")
        finally:
            if not settings.headless:
                page.wait_for_timeout(2000)
            browser.close()

    return report
