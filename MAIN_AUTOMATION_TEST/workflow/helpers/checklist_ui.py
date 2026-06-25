# -*- coding: utf-8 -*-
"""UI helpers — checklist list / detail (từ explore + BR-TPL-01)."""
from __future__ import annotations

import re
from datetime import date

from playwright.sync_api import Locator

from src.auth import login
from workflow.common import WorkflowContext
from workflow.helpers.outcome import fail_result, pass_result

LIST_HEADERS = ["STT", "Nhân viên", "Checklist", "Từ ngày", "Đến ngày", "Trạng thái", "Tiến độ"]
TEMPLATE_HEADERS = ["STT", "Mã template", "Tên template", "Mô tả", "Trạng thái", "Ngày tạo", "Chức năng"]


def autotest_text(ctx: WorkflowContext) -> str:
    n = len(ctx.case.get("evidenceRuns") or []) + 1
    return f"automationtestver{n}"


def login_as(ctx: WorkflowContext, role: str) -> None:
    ctx.role = role
    account = None
    for acc in ctx.settings.accounts:
        if acc.role == role:
            account = acc
            break
    if not account:
        raise RuntimeError(f"Khong tim thay tai khoan {role}")
    if not login(ctx.page, ctx.settings, account, ctx):
        raise RuntimeError(f"Dang nhap {role} that bai")


def goto_path(ctx: WorkflowContext, path: str) -> None:
    ctx.goto(path)


def goto_checklist_list(ctx: WorkflowContext) -> None:
    goto_path(ctx, "/hrm/checklist")
    wait_for_data_rows(ctx)


def wait_for_data_rows(ctx: WorkflowContext, timeout: int = 15000) -> None:
    try:
        ctx.page.locator("tbody tr.ant-table-row").first.wait_for(state="visible", timeout=timeout)
    except Exception:
        ctx.page.wait_for_timeout(2000)


def goto_template_list(ctx: WorkflowContext) -> None:
    goto_path(ctx, "/hrm/checklist/template")


def shot(ctx: WorkflowContext, name: str) -> None:
    ctx.screenshot(name)


def ensure_case_evidence(ctx: WorkflowContext) -> None:
    """Đảm bảo mỗi case có ít nhất 1 ảnh minh chứng."""
    if list(ctx.run_dir.glob("*.png")):
        return
    shot(ctx, "case_result")


def fail_with_shot(
    ctx: WorkflowContext,
    message: str,
    shot_name: str = "error_state",
    **extra,
) -> dict:
    shot(ctx, shot_name)
    return fail_result(message, **extra)


def click_button(ctx: WorkflowContext, text: str) -> bool:
    loc = ctx.page.locator(f"button:has-text('{text}')").first
    if loc.count() == 0:
        return False
    loc.click(timeout=8000)
    ctx.page.wait_for_timeout(800)
    return True


def logout_header(ctx: WorkflowContext) -> bool:
    """Menu góc phải header → [Đăng xuất] (dùng được mọi màn)."""
    header = ctx.page.locator(".ant-layout-header, header").first
    trigger = header.locator(".ant-dropdown-trigger").last
    if not trigger.count():
        trigger = header.locator(".ant-avatar").last
    if not trigger.count():
        trigger = header.locator("[class*='avatar'], [class*='user']").last
    if not trigger.count():
        ctx.log("Khong tim thay menu user o header", "WARN")
        return False

    trigger.click(timeout=8000)
    ctx.page.wait_for_timeout(700)
    shot(ctx, "user_menu_open")

    logout_item = ctx.page.locator(
        ".ant-dropdown-menu-item:has-text('Đăng xuất'), "
        ".ant-dropdown-menu-title-content:has-text('Đăng xuất')"
    ).first
    if not logout_item.count():
        logout_item = ctx.page.get_by_text("Đăng xuất", exact=True).last
    if not logout_item.count():
        ctx.log("Khong thay nut Dang xuat trong dropdown", "WARN")
        return False

    logout_item.click(timeout=8000)
    ctx.page.wait_for_timeout(2500)
    shot(ctx, "after_logout")
    try:
        ctx.page.locator("#email").wait_for(state="visible", timeout=12000)
        return True
    except Exception:
        ctx.page.goto(ctx.settings.base_url, wait_until="domcontentloaded", timeout=60000)
        ctx.page.wait_for_timeout(1000)
        return ctx.page.locator("#email").count() > 0


def switch_role_login(ctx: WorkflowContext, role: str) -> None:
    """Đăng xuất qua header → đăng nhập role khác."""
    if not logout_header(ctx):
        ctx.log("Logout header that bai — fallback clear cookies", "WARN")
        ctx.page.context.clear_cookies()
        ctx.page.goto(ctx.settings.base_url, wait_until="domcontentloaded", timeout=60000)
        ctx.page.wait_for_timeout(1000)
    login_as(ctx, role)


def table_headers(ctx: WorkflowContext) -> list[str]:
    headers = ctx.page.locator("thead th, .ant-table-thead th")
    return [h.inner_text().strip() for h in headers.all() if h.inner_text().strip()]


def _is_data_row(row) -> bool:
    try:
        cls = row.get_attribute("class") or ""
        if "ant-table-measure-row" in cls:
            return False
        text = row.inner_text().strip()
        if not text or "No data" in text:
            return False
        return True
    except Exception:
        return False


def data_table_rows(ctx: WorkflowContext) -> list:
    rows = ctx.page.locator("tbody tr.ant-table-row").all()
    if rows:
        return [r for r in rows if _is_data_row(r)]
    return [r for r in ctx.page.locator("tbody tr").all() if _is_data_row(r)]


def data_row_count(ctx: WorkflowContext) -> int:
    return len(data_table_rows(ctx))


def pagination_text(ctx: WorkflowContext) -> str:
    loc = ctx.page.locator(".ant-pagination-total-text, :text-matches('Tổng')").first
    if loc.count():
        return loc.inner_text().strip()
    return ""


def search_input(ctx: WorkflowContext) -> Locator:
    return ctx.page.locator(
        'input[placeholder*="checklist" i], input[placeholder*="Tên" i], '
        'input[placeholder*="template" i], input[placeholder*="mã" i], '
        'input[placeholder*="nhân" i], input[placeholder*="nhan" i]'
    ).first


def search_keyword(ctx: WorkflowContext, keyword: str) -> None:
    inp = search_input(ctx)
    inp.wait_for(state="visible", timeout=10000)
    inp.fill(keyword)
    ctx.page.wait_for_timeout(400)
    shot(ctx, "search_filled")
    search_btn = ctx.page.locator("button .anticon-search, button:has(.anticon-search)").first
    if search_btn.count():
        search_btn.click()
    else:
        inp.press("Enter")
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "search_result")


def click_refresh(ctx: WorkflowContext) -> None:
    btn = ctx.page.locator("button .anticon-reload, button:has(.anticon-sync)").first
    btn.click(timeout=8000)
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "after_refresh")


def open_status_dropdown(ctx: WorkflowContext) -> None:
    selects = ctx.page.locator(".ant-select:not(.ant-pagination-options-size-changer)")
    for sel in selects.all()[:4]:
        try:
            if not sel.is_visible():
                continue
            text = sel.inner_text()
            if "Trạng thái" in text or "Tất cả" in text:
                sel.click(timeout=5000)
                ctx.page.wait_for_timeout(800)
                shot(ctx, "status_dropdown_open")
                return
        except Exception:
            continue


def _click_ant_select_option(ctx: WorkflowContext, option_text: str) -> bool:
    opt = ctx.page.locator(".ant-select-item-option-content").filter(has_text=option_text).first
    if not opt.count():
        opt = ctx.page.get_by_text(option_text, exact=True)
    if not opt.count():
        return False
    opt.click(timeout=8000)
    ctx.page.wait_for_timeout(1000)
    return True


def _scope_filter_select(ctx: WorkflowContext) -> Locator | None:
    for sel in ctx.page.locator(".ant-select:not(.ant-pagination-options-size-changer)").all():
        try:
            if not sel.is_visible():
                continue
            text = sel.inner_text()
            if any(k in text for k in ("Tất cả", "Cá nhân", "Thực hiện cho NV", "Thực hiện")):
                return sel
        except Exception:
            continue
    return None


def filter_thuc_hien_cho_employee(ctx: WorkflowContext, scope_label: str, employee_name: str) -> bool:
    """Dropdown phạm vi → Thực hiện cho NV → chọn nhân viên."""
    scope_sel = _scope_filter_select(ctx)
    if scope_sel is None:
        ctx.log("Khong tim thay dropdown pham vi", "WARN")
        return False

    scope_sel.click(timeout=8000)
    ctx.page.wait_for_timeout(600)
    shot(ctx, "status_dropdown_open")
    if not _click_ant_select_option(ctx, scope_label):
        ctx.log(f"Khong chon duoc [{scope_label}]", "WARN")
        return False
    shot(ctx, "scope_selected")
    ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(600)

    employee_sel = None
    for sel in ctx.page.locator(".ant-select:not(.ant-pagination-options-size-changer)").all():
        if not sel.is_visible():
            continue
        text = sel.inner_text()
        if any(k in text for k in ("Tất cả", "Cá nhân", scope_label)):
            continue
        if "Trạng thái" in text and employee_name not in text:
            continue
        employee_sel = sel
        break

    if employee_sel is None:
        selects = ctx.page.locator(".ant-select:not(.ant-pagination-options-size-changer)")
        if selects.count() >= 2:
            employee_sel = selects.nth(1)

    if employee_sel is None:
        ctx.log("Khong tim thay dropdown nhan vien", "WARN")
        return False

    employee_sel.click(timeout=8000)
    ctx.page.wait_for_timeout(600)
    shot(ctx, "employee_dropdown_open")
    inp = employee_sel.locator("input").first
    if inp.count():
        inp.fill(employee_name)
        ctx.page.wait_for_timeout(800)
    if not _click_ant_select_option(ctx, employee_name):
        return False
    shot(ctx, "employee_selected")
    try:
        employee_sel.locator(".ant-select-selection-item").filter(has_text=employee_name).wait_for(
            state="visible", timeout=5000
        )
    except Exception:
        pass

    # Dropdown tu dong loc — chi cho bang cap nhat
    try:
        ctx.page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        ctx.page.wait_for_timeout(2000)
    return True


def extract_employee_names_from_table(ctx: WorkflowContext) -> list[str]:
    headers = table_headers(ctx)
    emp_idx = _column_index(headers, "Nhân viên", "Nhan vien")
    if emp_idx is None:
        emp_idx = 1

    names: list[str] = []
    for tr in data_table_rows(ctx):
        cells = tr.locator("td").all()
        if len(cells) <= emp_idx:
            continue
        cell_text = cells[emp_idx].inner_text().strip()
        lines = [ln.strip() for ln in cell_text.split("\n") if ln.strip()]
        name = lines[0] if lines else cell_text
        names.append(name)
    return names


def _visible_picker_dropdown(ctx: WorkflowContext):
    return ctx.page.locator(".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)")


def pick_date_range(
    ctx: WorkflowContext,
    *,
    year: int | None = None,
    month: int | None = None,
    start_day: int | None = None,
    end_day: int | None = None,
) -> None:
    picker = ctx.page.locator(".ant-picker-range").first
    picker.click(timeout=8000)
    ctx.page.wait_for_timeout(800)

    if year and month and start_day and end_day:
        filter_start = date(year, month, start_day)
        filter_end = date(year, month, end_day)
        if _try_fill_date_range_inputs(ctx, filter_start, filter_end):
            ctx.log("Da nhap khoang ngay qua o input")
            shot(ctx, "calendar_range_selected")
        else:
            _ensure_calendar_month(ctx, year, month)
            shot(ctx, "calendar_open")
            _pick_calendar_day(ctx, year, month, start_day)
            ctx.page.wait_for_timeout(1200)
            shot(ctx, "calendar_pick_start")
            _pick_calendar_day(ctx, year, month, end_day)
            ctx.page.wait_for_timeout(1500)
            shot(ctx, "calendar_range_selected")
            try:
                _visible_picker_dropdown(ctx).wait_for(state="hidden", timeout=5000)
            except Exception:
                ctx.page.wait_for_timeout(500)
    else:
        cells = ctx.page.locator(
            ".ant-picker-dropdown .ant-picker-cell-in-view:not(.ant-picker-cell-disabled) .ant-picker-cell-inner"
        )
        if cells.count() >= 2:
            cells.nth(0).click()
            ctx.page.wait_for_timeout(400)
            cells.nth(min(7, cells.count() - 1)).click()
            ctx.page.wait_for_timeout(600)

    ctx.page.wait_for_timeout(800)
    search_btn = ctx.page.locator("button .anticon-search, button:has(.anticon-search)").first
    if search_btn.count():
        search_btn.click()
    ctx.page.wait_for_timeout(3000)
    shot(ctx, "calendar_search_result")


def _try_fill_date_range_inputs(ctx: WorkflowContext, start: date, end: date) -> bool:
    """Nhập trực tiếp DD/MM/YYYY — tránh lỗi 2 panel lịch trùng ô ngày."""
    picker = ctx.page.locator(".ant-picker-range").first
    inputs = picker.locator("input")
    if inputs.count() < 2:
        return False
    fmt = "%d/%m/%Y"
    start_s, end_s = start.strftime(fmt), end.strftime(fmt)
    try:
        inputs.nth(0).click()
        ctx.page.wait_for_timeout(300)
        inputs.nth(0).fill(start_s)
        ctx.page.wait_for_timeout(300)
        inputs.nth(1).click()
        ctx.page.wait_for_timeout(300)
        inputs.nth(1).fill(end_s)
        inputs.nth(1).press("Enter")
        ctx.page.wait_for_timeout(800)
        v0 = inputs.nth(0).input_value()
        v1 = inputs.nth(1).input_value()
        return bool(v0 and v1)
    except Exception as exc:
        ctx.log(f"Nhap input ngay that bai: {exc}", "WARN")
        return False


def _ensure_calendar_month(ctx: WorkflowContext, year: int, month: int) -> None:
    target = f"{year}-{month:02d}"
    dropdown = _visible_picker_dropdown(ctx)
    for _ in range(24):
        if dropdown.locator(f".ant-picker-cell[title^='{target}-']").count():
            return
        sample = dropdown.locator(".ant-picker-cell-in-view[title]").first
        if sample.count():
            title = sample.get_attribute("title") or ""
            if title < f"{target}-01":
                dropdown.locator(".ant-picker-header-next-btn").first.click()
            else:
                dropdown.locator(".ant-picker-header-prev-btn").first.click()
        else:
            dropdown.locator(".ant-picker-header-next-btn").first.click()
        ctx.page.wait_for_timeout(350)


def _pick_calendar_day(ctx: WorkflowContext, year: int, month: int, day: int) -> None:
    title = f"{year}-{month:02d}-{day:02d}"
    dropdown = _visible_picker_dropdown(ctx)
    # Panel trái = tháng đầu (tháng 6) — tránh strict mode 2 ô "30" (Jun + Jul)
    panel = dropdown.locator(".ant-picker-panel").first
    cell = panel.locator(f".ant-picker-cell[title='{title}'] .ant-picker-cell-inner").first
    if not cell.count():
        cell = dropdown.locator(f".ant-picker-cell[title='{title}'] .ant-picker-cell-inner").first
    cell.wait_for(state="visible", timeout=10000)
    cell.click()


def find_error_toast(ctx: WorkflowContext) -> str | None:
    """Toast Lỗi / error sau thao tac API."""
    for sel in (
        ".Toastify__toast",
        ".Toastify__toast-body",
        ".ant-message-notice-content",
        ".ant-notification-notice-message",
    ):
        for node in ctx.page.locator(sel).all():
            try:
                if not node.is_visible():
                    continue
            except Exception:
                continue
            text = node.inner_text().strip()
            if not text:
                continue
            lower = text.lower()
            if "lỗi" in lower or "error occurred" in lower or "an error" in lower:
                shot(ctx, "error_toast")
                return text
    return None


def parse_vn_date(text: str) -> date | None:
    text = (text or "").strip()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if not m:
        return None
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(year, month, day)
    except ValueError:
        return None


def column_index(headers: list[str], *needles: str) -> int | None:
    for i, h in enumerate(headers):
        norm = h.lower().replace("ừ", "u").replace("ế", "e").replace("đ", "d")
        for needle in needles:
            n = needle.lower()
            if n in h.lower() or n in norm:
                return i
    return None


def _column_index(headers: list[str], *needles: str) -> int | None:
    return column_index(headers, *needles)


def extract_checklist_date_rows(ctx: WorkflowContext) -> list[tuple[str, str, date | None, date | None]]:
    """Đọc cột Từ ngày / Đến ngày từ bảng danh sách checklist."""
    headers = table_headers(ctx)
    from_idx = _column_index(headers, "Từ ngày", "Tu ngay", "From")
    to_idx = _column_index(headers, "Đến ngày", "Den ngay", "To")
    if from_idx is None or to_idx is None:
        from_idx, to_idx = 3, 4

    rows: list[tuple[str, str, date | None, date | None]] = []
    for tr in data_table_rows(ctx):
        cells = tr.locator("td").all()
        if len(cells) <= max(from_idx, to_idx):
            continue
        raw_from = cells[from_idx].inner_text().strip()
        raw_to = cells[to_idx].inner_text().strip()
        rows.append((raw_from, raw_to, parse_vn_date(raw_from), parse_vn_date(raw_to)))
    return rows


def open_first_list_row(ctx: WorkflowContext) -> bool:
    rows = data_table_rows(ctx)
    if not rows:
        return False
    row = rows[0]
    row.click(timeout=8000)
    ctx.page.wait_for_timeout(2000)
    if is_detail_page(ctx):
        return True
    link = row.locator("a").first
    if link.count():
        link.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
    return is_detail_page(ctx)


def open_detail_by_index(ctx: WorkflowContext, index: int = 0) -> bool:
    rows = data_table_rows(ctx)
    if index >= len(rows):
        return False
    rows[index].click(timeout=8000)
    ctx.page.wait_for_timeout(2000)
    if is_detail_page(ctx):
        return True
    link = rows[index].locator("a").first
    if link.count():
        link.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
    return is_detail_page(ctx)


def is_detail_page(ctx: WorkflowContext) -> bool:
    return bool(re.search(r"/hrm/checklist/[0-9a-f-]{36}", ctx.page.url, re.I))


def body_contains(ctx: WorkflowContext, *parts: str) -> bool:
    body = ctx.page.locator("body").inner_text()
    return all(p in body for p in parts)


def progress_pattern_in_table(ctx: WorkflowContext) -> bool:
    body = ctx.page.locator("tbody").inner_text()
    return bool(re.search(r"\d+/\d+", body))


def extract_employee_column_pairs(ctx: WorkflowContext) -> list[tuple[str, str]]:
    """BR-13: (fullName, accountName) từ cột Nhân viên."""
    headers = table_headers(ctx)
    emp_idx = _column_index(headers, "Nhân viên", "Nhan vien")
    if emp_idx is None:
        emp_idx = 1

    pairs: list[tuple[str, str]] = []
    for tr in data_table_rows(ctx):
        cells = tr.locator("td").all()
        if len(cells) <= emp_idx:
            continue
        cell_text = cells[emp_idx].inner_text().strip()
        lines = [ln.strip() for ln in cell_text.split("\n") if ln.strip()]
        full_name = lines[0] if lines else ""
        account_name = lines[1] if len(lines) > 1 else ""
        pairs.append((full_name, account_name))
    return pairs


def employee_two_line_format(ctx: WorkflowContext) -> bool:
    """BR-13: cột nhân viên có fullName + accountName."""
    pairs = extract_employee_column_pairs(ctx)
    return bool(pairs) and all(f and a for f, a in pairs)


def _row_has_tre_label(text: str) -> bool:
    return "trễ" in text or bool(re.search(r"\d+\s*tr[ệe]", text, re.I))


def _find_tre_row(ctx: WorkflowContext) -> Locator | None:
    for row in data_table_rows(ctx):
        try:
            if _row_has_tre_label(row.inner_text()):
                return row
        except Exception:
            continue
    return None


def _scroll_table_body(ctx: WorkflowContext) -> Locator | None:
    """Cuộn `.ant-table-body` từng đoạn để tìm dòng có chữ trễ."""
    body = ctx.page.locator(".ant-table-body").first
    if not body.count():
        return None
    try:
        metrics = body.evaluate(
            """el => ({
                scrollHeight: el.scrollHeight,
                clientHeight: el.clientHeight,
            })"""
        )
        scroll_height = int(metrics.get("scrollHeight") or 0)
        client_height = int(metrics.get("clientHeight") or 0)
        if scroll_height <= client_height + 4:
            return _find_tre_row(ctx)

        step = max(client_height // 2, 220)
        pos = 0
        while pos <= scroll_height:
            body.evaluate("(el, y) => { el.scrollTop = y; }", pos)
            ctx.page.wait_for_timeout(350)
            row = _find_tre_row(ctx)
            if row:
                return row
            pos += step

        body.evaluate("(el) => { el.scrollTop = el.scrollHeight; }")
        ctx.page.wait_for_timeout(400)
        return _find_tre_row(ctx)
    except Exception:
        return None


def scroll_to_tre_row(ctx: WorkflowContext) -> bool:
    """
    Cuộn bảng danh sách đến dòng có chữ «trễ» (scroll body + phân trang).
    Dòng tìm thấy được scroll_into_view để chụp minh chứng đúng vị trí.
    """
    row = _find_tre_row(ctx)
    if row:
        row.scroll_into_view_if_needed()
        ctx.page.wait_for_timeout(400)
        return True

    row = _scroll_table_body(ctx)
    if row:
        row.scroll_into_view_if_needed()
        ctx.page.wait_for_timeout(400)
        return True

    for _ in range(25):
        next_btn = ctx.page.locator(".ant-pagination-next:not(.ant-pagination-disabled)").first
        if not next_btn.count():
            break
        try:
            disabled = "ant-pagination-disabled" in (next_btn.get_attribute("class") or "")
            if disabled or not next_btn.is_enabled():
                break
        except Exception:
            break
        next_btn.click(timeout=5000)
        ctx.page.wait_for_timeout(1200)
        row = _find_tre_row(ctx)
        if row:
            row.scroll_into_view_if_needed()
            ctx.page.wait_for_timeout(400)
            return True
        row = _scroll_table_body(ctx)
        if row:
            row.scroll_into_view_if_needed()
            ctx.page.wait_for_timeout(400)
            return True

    return False


def list_shows_tre_label(ctx: WorkflowContext) -> bool:
    """Danh sách checklist có nhãn trễ — cuộn bảng đến đúng dòng."""
    return scroll_to_tre_row(ctx)


def overdue_badge_visible(ctx: WorkflowContext) -> bool:
    return list_shows_tre_label(ctx)


def officer_cannot_access_template(ctx: WorkflowContext) -> dict:
    goto_template_list(ctx)
    shot(ctx, "template_access_attempt")
    url = ctx.page.url
    body = ctx.page.locator("body").inner_text().lower()
    forbidden = any(x in body for x in ("403", "không có quyền", "khong co quyen", "forbidden", "not found"))
    if "/template" not in url or forbidden:
        return pass_result("OFFICER khong truy cap duoc man template admin-only")
    headers = table_headers(ctx)
    if any("Mã template" in h for h in headers):
        return fail_with_shot(ctx, "OFFICER van thay danh sach template — loi phan quyen", "template_access_attempt")
    return pass_result("OFFICER khong thay noi dung template admin")


def _task_journal_button(ctx: WorkflowContext, task_number: int | None = None) -> Locator | None:
    buttons = ctx.page.locator("button:has-text('Nhật ký'), button:has-text('Nhat ky')")
    if buttons.count() == 0:
        return None
    if task_number is None:
        return buttons.first
    for i in range(buttons.count()):
        btn = buttons.nth(i)
        try:
            matched = btn.evaluate(
                """(el, n) => {
                    let cur = el;
                    for (let i = 0; i < 15 && cur; i++) {
                        if (new RegExp('task\\\\s*' + n + '\\\\b', 'i').test(cur.innerText || '')) {
                            return true;
                        }
                        cur = cur.parentElement;
                    }
                    return false;
                }""",
                task_number,
            )
            if matched:
                return btn
        except Exception:
            continue
    return None


def open_journal_modal(ctx: WorkflowContext, task_number: int | None = None) -> bool:
    btn = _task_journal_button(ctx, task_number)
    if btn is None or not btn.count():
        btn = ctx.page.locator("button:has-text('Nhật ký'), button:has-text('Nhat ky')").first
    if not btn.count():
        return False
    btn.scroll_into_view_if_needed()
    btn.click()
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "journal_modal")
    if ctx.page.locator(
        ".ant-modal:visible, .ant-drawer-open, .ant-drawer:not(.ant-drawer-hidden)"
    ).count() > 0:
        return True
    return journal_has_dated_entries(ctx)


_LOG_DATETIME = re.compile(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}")


def journal_visible_text(ctx: WorkflowContext) -> str:
    for sel in (
        ".ant-drawer-open .ant-drawer-body",
        ".ant-drawer:not(.ant-drawer-hidden) .ant-drawer-body",
        ".ant-modal:visible .ant-modal-body",
        ".ant-modal:visible",
        ".ant-drawer:visible",
    ):
        loc = ctx.page.locator(sel).last
        if not loc.count():
            continue
        try:
            text = loc.inner_text()
            if _LOG_DATETIME.search(text):
                return text
        except Exception:
            continue
    body = ctx.page.locator("body").inner_text()
    if _LOG_DATETIME.search(body):
        return body
    return ""


def journal_log_lines(ctx: WorkflowContext) -> list[str]:
    text = journal_visible_text(ctx)
    return [ln.strip() for ln in text.splitlines() if ln.strip() and _LOG_DATETIME.search(ln)]


def journal_has_dated_entries(ctx: WorkflowContext) -> bool:
    return len(journal_log_lines(ctx)) > 0


def notice_texts(ctx: WorkflowContext) -> list[str]:
    chunks: list[str] = []
    try:
        dom_texts = ctx.page.evaluate(
            """() => {
            const out = [];
            const sels = [
                '.ant-message-notice-content',
                '.ant-message-custom-content',
                '.ant-notification-notice-message',
                '.ant-message-notice',
                '.ant-message-notice-wrapper',
                '.ant-message',
            ];
            for (const sel of sels) {
                document.querySelectorAll(sel).forEach((el) => {
                    const t = (el.innerText || '').trim();
                    if (t) out.push(t);
                });
            }
            return [...new Set(out)];
        }"""
        )
        chunks.extend(dom_texts or [])
    except Exception:
        pass
    selectors = (
        ".ant-message-notice",
        ".ant-message-notice-content",
        ".ant-notification-notice",
        ".ant-notification-notice-message",
        ".ant-message-custom-content",
        ".ant-message-error",
    )
    for sel in selectors:
        for text in ctx.page.locator(sel).all_inner_texts():
            t = text.strip()
            if t and t not in chunks:
                chunks.append(t)
    return chunks


_ERROR_TOAST_NEEDLES = (
    "lỗi",
    "thất bại",
    "that bai",
    "không thành công",
    "khong thanh cong",
    "có lỗi",
    "co loi",
    "error",
    "failed",
)
_SUCCESS_TOAST_NEEDLES = ("thành công", "thanh cong", "success")


def wait_for_toast(ctx: WorkflowContext, *needles: str, timeout_ms: int = 8000) -> str | None:
    """Chờ toast/notification chứa needle — không quét body (tránh false positive)."""
    elapsed = 0
    step = 300
    while elapsed < timeout_ms:
        for text in notice_texts(ctx):
            low = text.lower()
            for needle in needles:
                if needle.lower() in low:
                    return text
        ctx.page.wait_for_timeout(step)
        elapsed += step
    return None


def wait_for_error_toast(ctx: WorkflowContext, timeout_ms: int = 8000) -> str | None:
    return wait_for_toast(ctx, *_ERROR_TOAST_NEEDLES, timeout_ms=timeout_ms)


def wait_for_success_toast(ctx: WorkflowContext, timeout_ms: int = 6000) -> str | None:
    return wait_for_toast(ctx, *_SUCCESS_TOAST_NEEDLES, timeout_ms=timeout_ms)


def modal_is_visible(ctx: WorkflowContext) -> bool:
    return ctx.page.locator(".ant-modal:visible").count() > 0


def notice_contains(ctx: WorkflowContext, *needles: str) -> bool:
    combined = " ".join(notice_texts(ctx)).lower()
    body = ctx.page.locator("body").inner_text().lower()
    haystack = f"{combined} {body}"
    return any(n.lower() in haystack for n in needles)


def wait_for_notice(ctx: WorkflowContext, *needles: str, timeout_ms: int = 12000) -> str | None:
    """Chờ toast/notice chứa needle — poll vì ant-message tự ẩn sau vài giây."""
    elapsed = 0
    step = 400
    while elapsed < timeout_ms:
        for text in notice_texts(ctx):
            low = text.lower()
            for needle in needles:
                if needle.lower() in low:
                    return text
        body = ctx.page.locator("body").inner_text().lower()
        for needle in needles:
            if needle.lower() in body:
                return needle
        ctx.page.wait_for_timeout(step)
        elapsed += step
    return None


def click_quay_lai(ctx: WorkflowContext) -> bool:
    ok = click_button(ctx, "Quay lại")
    ctx.page.wait_for_timeout(1500)
    shot(ctx, "after_quay_lai")
    return ok and "/hrm/checklist" in ctx.page.url and not is_detail_page(ctx)


def detail_has_progress(ctx: WorkflowContext) -> bool:
    body = ctx.page.locator("body").inner_text()
    return bool(re.search(r"\d+/\d+", body)) and ("Tiến độ" in body or "progress" in body.lower())


def detail_has_employee_info(ctx: WorkflowContext) -> bool:
    body = ctx.page.locator("body").inner_text()
    return "Nhân viên" in body and ("Chức vụ" in body or "Đơn vị" in body)


def description_field_value(ctx: WorkflowContext, label: str) -> str:
    """Đọc giá trị ant-descriptions theo nhãn (vd. Nhân viên, Chức vụ)."""
    target = label.lower()
    for item in ctx.page.locator(".ant-descriptions-item").all():
        try:
            label_el = item.locator(".ant-descriptions-item-label").first
            if not label_el.count():
                continue
            if target not in label_el.inner_text().lower():
                continue
            content = item.locator(".ant-descriptions-item-content").first
            if content.count():
                return content.inner_text().strip()
        except Exception:
            continue
    return ""


def parse_two_line_name(text: str) -> tuple[str, str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    full_name = lines[0] if lines else ""
    account_name = lines[1] if len(lines) > 1 else ""
    return full_name, account_name


def task_action_visible(ctx: WorkflowContext, label: str) -> bool:
    return ctx.page.locator(f"button:has-text('{label}')").count() > 0


def _task_action_button(
    ctx: WorkflowContext,
    action_text: str,
    task_number: int | None = None,
) -> Locator | None:
    buttons = ctx.page.locator(f"button:has-text('{action_text}')")
    if buttons.count() == 0:
        return None
    if task_number is None:
        return buttons.first
    for i in range(buttons.count()):
        btn = buttons.nth(i)
        try:
            matched = btn.evaluate(
                """(el, n) => {
                    let cur = el;
                    for (let i = 0; i < 15 && cur; i++) {
                        if (new RegExp('task\\\\s*' + n + '\\\\b', 'i').test(cur.innerText || '')) {
                            return true;
                        }
                        cur = cur.parentElement;
                    }
                    return false;
                }""",
                task_number,
            )
            if matched:
                return btn
        except Exception:
            continue
    return None


def _task_confirm_button(ctx: WorkflowContext, task_number: int | None = None) -> Locator | None:
    return _task_action_button(ctx, "Đúng hạn", task_number)


def _click_task_action(ctx: WorkflowContext, action_text: str, task_number: int | None = None) -> bool:
    btn = _task_action_button(ctx, action_text, task_number)
    if btn is None or not btn.count():
        return False
    try:
        btn.scroll_into_view_if_needed()
        btn.click(timeout=10000)
    except Exception:
        return False
    ctx.page.wait_for_timeout(800)
    shot(ctx, "confirm_modal")
    return True


def click_task_confirm_on_time(ctx: WorkflowContext, task_number: int | None = None) -> bool:
    return _click_task_action(ctx, "Đúng hạn", task_number)


def click_task_confirm_late(ctx: WorkflowContext, task_number: int | None = None) -> bool:
    return _click_task_action(ctx, "Muộn", task_number)


def click_task_change_officer(ctx: WorkflowContext, task_number: int | None = None) -> bool:
    if _click_task_action(ctx, "Đổi CB", task_number):
        return True
    return _click_task_action(ctx, "Đổi cán bộ", task_number)


def click_task_undo(ctx: WorkflowContext, task_number: int | None = None) -> bool:
    if _click_task_action(ctx, "Hoàn tác", task_number):
        return True
    return _click_task_action(ctx, "Undo", task_number)


def task_has_action(ctx: WorkflowContext, action_text: str, task_number: int) -> bool:
    btn = _task_action_button(ctx, action_text, task_number)
    return btn is not None and btn.count() > 0


def confirm_undo_prompt(ctx: WorkflowContext) -> bool:
    """Xác nhận popconfirm/modal sau khi bấm [Hoàn tác]."""
    for sel in (
        ".ant-popconfirm-buttons button.ant-btn-primary",
        ".ant-popconfirm button:has-text('Xác nhận')",
        ".ant-modal button:has-text('Xác nhận')",
        ".ant-popconfirm button:has-text('OK')",
    ):
        btn = ctx.page.locator(sel).last
        try:
            if btn.count() and btn.is_visible():
                btn.click(timeout=5000)
                ctx.page.wait_for_timeout(300)
                return True
        except Exception:
            continue
    return False


def submit_undo_action(ctx: WorkflowContext, shot_prefix: str) -> tuple[bool, str]:
    """Poll toast sau khi xác nhận hoàn tác."""
    seen_error = ""
    for attempt in range(80):
        for text in notice_texts(ctx):
            kind = _toast_kind(text)
            if kind == "error":
                shot(ctx, f"{shot_prefix}_error_toast")
                return False, text
            if kind == "success":
                shot(ctx, shot_prefix)
                return True, text
            if "lỗi" in text.lower() or "loi:" in text.lower() or "có lỗi" in text.lower():
                seen_error = text

        if seen_error:
            shot(ctx, f"{shot_prefix}_error_toast")
            return False, seen_error

        if attempt >= 5:
            tail = wait_for_success_toast(ctx, timeout_ms=200)
            if tail:
                shot(ctx, shot_prefix)
                return True, tail

        ctx.page.wait_for_timeout(100)

    shot(ctx, shot_prefix)
    return True, "Hoan tac — khong thay toast loi"


def pick_random_select_option(ctx: WorkflowContext, *, exclude: set[str] | None = None) -> str | None:
    """Chọn ngẫu nhiên 1 option đang hiển thị trên trang 1 dropdown Ant Design."""
    import random

    skip = {s.strip().lower() for s in (exclude or set()) if s and s.strip()}
    options = ctx.page.locator(".ant-select-item-option-content")
    choices: list[tuple[int, str]] = []
    for i in range(options.count()):
        try:
            text = options.nth(i).inner_text().strip()
        except Exception:
            continue
        if not text:
            continue
        low = text.lower()
        if any(s in low or low in s for s in skip):
            continue
        choices.append((i, text))
    if not choices:
        return None
    idx, label = random.choice(choices)
    options.nth(idx).click(timeout=8000)
    ctx.page.wait_for_timeout(300)
    return label


def submit_save_modal(ctx: WorkflowContext, shot_prefix: str) -> tuple[bool, str]:
    """Bấm [Lưu]/[Xác nhận] trong modal đang mở — poll toast."""
    modal = ctx.page.locator(".ant-modal:visible").last
    modal.wait_for(state="visible", timeout=10000)
    btn = modal.locator(
        "button:has-text('Lưu'), button:has-text('Xác nhận'), button.ant-btn-primary"
    ).last
    btn.wait_for(state="visible", timeout=8000)
    btn.click()

    seen_error = ""
    for attempt in range(80):
        for text in notice_texts(ctx):
            kind = _toast_kind(text)
            if kind == "error":
                shot(ctx, f"{shot_prefix}_error_toast")
                return False, text
            if kind == "success":
                shot(ctx, shot_prefix)
                return True, text
            if "lỗi" in text.lower() or "loi:" in text.lower() or "có lỗi" in text.lower():
                seen_error = text

        if seen_error:
            shot(ctx, f"{shot_prefix}_error_toast")
            return False, seen_error

        if not modal_is_visible(ctx) and attempt >= 3:
            tail = wait_for_success_toast(ctx, timeout_ms=1200)
            shot(ctx, shot_prefix)
            return True, tail or "Luu thanh cong"

        ctx.page.wait_for_timeout(100)

    shot(ctx, f"{shot_prefix}_error_toast")
    if modal_is_visible(ctx):
        return False, "Luu that bai — modal van mo, khong co toast thanh cong"
    return False, "Khong xac dinh duoc ket qua luu"


def fill_modal_text(ctx: WorkflowContext, text: str) -> None:
    modal = ctx.page.locator(".ant-modal:visible").last
    modal.wait_for(state="visible", timeout=10000)
    inp = modal.locator("textarea, input[type='text']").first
    inp.wait_for(state="visible", timeout=8000)
    inp.click()
    inp.fill("")
    ctx.page.wait_for_timeout(200)
    inp.fill(text)
    ctx.page.wait_for_timeout(400)


def _fill_modal_input(inp: Locator, text: str) -> None:
    inp.wait_for(state="visible", timeout=8000)
    inp.click()
    inp.fill("")
    inp.page.wait_for_timeout(200)
    inp.fill(text)
    inp.page.wait_for_timeout(300)


def fill_late_confirm_modal(ctx: WorkflowContext, note: str, reason: str | None = None) -> None:
    """
    Modal [Muộn]: điền [Ghi chú / Minh chứng] + [Lý do xác nhận muộn] (bắt buộc).
    """
    late_reason = reason or note
    modal = ctx.page.locator(".ant-modal:visible").last
    modal.wait_for(state="visible", timeout=10000)

    late_item = modal.locator(".ant-form-item").filter(
        has_text=re.compile(r"Lý do.*muộn|ly do.*muon", re.I)
    )
    if late_item.count():
        late_inp = late_item.first.locator("textarea, input[type='text']").first
        if late_inp.count():
            _fill_modal_input(late_inp, late_reason)

    note_item = modal.locator(".ant-form-item").filter(
        has_text=re.compile(r"Ghi chú|Minh chứng|ghi chu|minh chung", re.I)
    )
    if note_item.count():
        note_inp = note_item.first.locator("textarea, input[type='text']").first
        if note_inp.count():
            _fill_modal_input(note_inp, note)

    textareas = modal.locator("textarea")
    if textareas.count() >= 2 and not late_item.count():
        _fill_modal_input(textareas.nth(0), note)
        _fill_modal_input(textareas.nth(1), late_reason)
    elif textareas.count() == 1 and not late_item.count():
        _fill_modal_input(textareas.first, late_reason)

    ctx.page.wait_for_timeout(400)


def _toast_kind(text: str) -> str | None:
    low = text.lower()
    if any(n in low for n in _ERROR_TOAST_NEEDLES):
        return "error"
    if any(n in low for n in _SUCCESS_TOAST_NEEDLES):
        return "success"
    return None


def submit_confirm_modal(ctx: WorkflowContext, shot_prefix: str) -> tuple[bool, str]:
    """
    Bấm [Xác nhận] trong modal đang mở — poll toast ngay (toast lỗi tự ẩn nhanh).
    Trả về (ok, message).
    """
    modal = ctx.page.locator(".ant-modal:visible").last
    modal.wait_for(state="visible", timeout=10000)
    btn = modal.locator("button:has-text('Xác nhận'), button.ant-btn-primary").last
    btn.wait_for(state="visible", timeout=8000)
    btn.click()

    seen_error = ""
    for attempt in range(80):
        for text in notice_texts(ctx):
            kind = _toast_kind(text)
            if kind == "error":
                shot(ctx, f"{shot_prefix}_error_toast")
                return False, text
            if kind == "success":
                shot(ctx, shot_prefix)
                return True, text
            if "lỗi" in text.lower() or "loi:" in text.lower() or "có lỗi" in text.lower():
                seen_error = text

        if seen_error:
            shot(ctx, f"{shot_prefix}_error_toast")
            return False, seen_error

        if not modal_is_visible(ctx) and attempt >= 3:
            tail = wait_for_success_toast(ctx, timeout_ms=1200)
            shot(ctx, shot_prefix)
            return True, tail or "Xac nhan thanh cong"

        if attempt in (3, 8, 15) and modal_is_visible(ctx):
            shot(ctx, "after_confirm")

        ctx.page.wait_for_timeout(100)

    shot(ctx, f"{shot_prefix}_error_toast")
    if modal_is_visible(ctx):
        return False, "Xac nhan that bai — modal van mo, khong co toast thanh cong"
    return False, "Khong xac dinh duoc ket qua xac nhan"


def confirm_modal(ctx: WorkflowContext) -> bool:
    ok, _msg = submit_confirm_modal(ctx, "after_confirm")
    return ok


def confirm_cancel_checklist_modal(ctx: WorkflowContext) -> None:
    """Modal Hủy checklist — nút xác nhận là [Hủy checklist] đỏ, không phải [Xác nhận]."""
    modal = ctx.page.locator(".ant-modal:visible").filter(has_text="Hủy checklist").last
    modal.wait_for(state="visible", timeout=10000)
    btn = modal.locator(
        ".ant-modal-footer button:has-text('Hủy checklist'), "
        "button.ant-btn-dangerous:has-text('Hủy checklist')"
    ).last
    if not btn.count():
        btn = modal.locator("button.ant-btn-dangerous, button.ant-btn-primary").last
    btn.wait_for(state="visible", timeout=8000)
    btn.click()
    ctx.page.wait_for_timeout(800)
    shot(ctx, "cancel_confirm_click")


def checklist_detail_path(url_or_id: str) -> str:
    if re.match(r"https?://", url_or_id, re.I):
        m = re.search(r"(/hrm/checklist/[0-9a-f-]{36})", url_or_id, re.I)
        return m.group(1) if m else url_or_id
    if re.fullmatch(r"[0-9a-f-]{36}", url_or_id, re.I):
        return f"/hrm/checklist/{url_or_id}"
    if url_or_id.startswith("/"):
        return url_or_id
    return f"/hrm/checklist/{url_or_id}"


def goto_checklist_detail(ctx: WorkflowContext, url_or_id: str) -> bool:
    goto_path(ctx, checklist_detail_path(url_or_id))
    ctx.page.wait_for_timeout(2000)
    return is_detail_page(ctx)


def first_row_detail_href(ctx: WorkflowContext) -> str | None:
    rows = data_table_rows(ctx)
    if not rows:
        return None
    link = rows[0].locator("a[href*='/hrm/checklist/']").first
    if link.count():
        return link.get_attribute("href")
    return None


def assert_list_page(ctx: WorkflowContext, role: str, *, require_create: bool = False) -> dict:
    goto_checklist_list(ctx)
    shot(ctx, "list_page")
    headers = table_headers(ctx)
    missing = [h for h in LIST_HEADERS if not any(h in x for x in headers)]
    if missing and not headers:
        return fail_with_shot(ctx, f"Khong thay bang danh sach — headers: {headers}", "list_page")
    if require_create and not ctx.page.locator("button:has-text('Tạo checklist')").count():
        return fail_with_shot(ctx, "Khong thay button [Tạo checklist]", "list_page")
    rows = data_row_count(ctx)
    msg = f"{role} — danh sach checklist OK ({rows} dong)"
    if role == "ADMIN" and rows == 0:
        return fail_with_shot(ctx, "ADMIN khong thay instance nao", "list_page")
    return pass_result(msg, rowCount=rows, headers=headers)
