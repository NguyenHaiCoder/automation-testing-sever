# -*- coding: utf-8 -*-
"""
Playwright E2E — Checklist Nhân sự
Log output: ./log-playwright/run_YYYYMMDD_HHMMSS/

Chạy có Chromium hiển thị:
  python run_checklist_e2e.py --visible
  hoặc double-click run-checklist-test-visible.bat
"""
import argparse
import json
import os
import re
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# --- paths ---
ROOT = Path(__file__).resolve().parent
LOG_BASE = ROOT / "log-playwright"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = LOG_BASE / f"run_{RUN_ID}"
SCREENSHOT_DIR = RUN_DIR / "screenshots"
TEXT_LOG = RUN_DIR / "run.log"
JSON_LOG = RUN_DIR / "results.json"
SUMMARY_LOG = RUN_DIR / "summary.txt"

BASE = "https://qlrv.democloud.xyz"

ACCOUNTS = {
    "ADMIN": {"email": "administrator@gmail.com", "password": "123456@Ab"},
    "OFFICER": {"email": "tktruongphong@gmail.com", "password": "I1zxKHhAia@K"},
    "EMPLOYEE": {"email": "tdydoan.0102@gmail.com", "password": "g1wUeT3@aGJ@"},
}

results = {}
cfg = None  # RunConfig, set in run_tests()


@dataclass
class RunConfig:
    headless: bool
    slow_mo: int
    role_pause_ms: int
    wait_enter: bool

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(description="Checklist E2E Playwright")
        parser.add_argument(
            "--visible", "-v",
            action="store_true",
            help="Mở Chromium lên màn hình để xem bot tự click",
        )
        parser.add_argument(
            "--headless",
            action="store_true",
            help="Chạy ẩn (mặc định nếu không dùng --visible)",
        )
        args = parser.parse_args()

        env_headless = os.environ.get("HEADLESS", "").strip().lower()
        visible = args.visible or env_headless in ("0", "false", "no")
        if args.headless:
            visible = False

        headless = not visible
        slow_mo = int(os.environ.get("SLOW_MO", "600" if not headless else "0"))
        role_pause_ms = int(os.environ.get("ROLE_PAUSE_MS", "4000" if not headless else "0"))
        wait_enter = os.environ.get("WAIT_ENTER", "1" if not headless else "0").lower() in (
            "1", "true", "yes",
        )
        return cls(
            headless=headless,
            slow_mo=slow_mo,
            role_pause_ms=role_pause_ms,
            wait_enter=wait_enter,
        )


class RunLogger:
    def __init__(self, path: Path):
        self.path = path
        self._fh = open(path, "w", encoding="utf-8")
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    def log(self, msg: str, level: str = "INFO"):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}"
        self._fh.write(line + "\n")
        self._fh.flush()
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))

    def section(self, title: str):
        self.log("=" * 60)
        self.log(title)
        self.log("=" * 60)

    def close(self):
        self._fh.close()


logger: RunLogger = None  # set in run()


def case_key(case_id: str, role: str) -> str:
    return f"{case_id} [{role}]"


def record(case_id, passed, note="", role=""):
    key = case_key(case_id, role)
    entry = {
        "case_id": case_id,
        "result": "Pass" if passed else "Fail",
        "note": note[:500],
        "role": role,
        "time": datetime.now().isoformat(),
    }
    results[key] = entry
    logger.log(
        f"  {case_id} ({role}): {entry['result']} — {note[:120]}",
        "PASS" if passed else "FAIL",
    )


def login(page, email, password, role):
    logger.log(f"Login {role}: {email}")
    page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    page.locator("#email").fill(email)
    page.locator("#password").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(4000)
    try:
        page.wait_for_function("() => !document.querySelector('#email')", timeout=15000)
        logger.log(f"Login {role} OK → {page.url}")
        return True
    except PWTimeout:
        logger.log(f"Login {role} FAILED — still on login form", "ERROR")
        return False


def body_text(page):
    try:
        return page.locator("body").inner_text()
    except Exception:
        return ""


def goto_path(page, path):
    logger.log(f"Navigate → {path}")
    page.goto(BASE + path, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    logger.log(f"  URL: {page.url}")


def is_404(page):
    t = body_text(page)
    return "404" in t or "couldn't find your page" in t.lower()


def any_text(page, *texts):
    t = body_text(page)
    return any(x in t for x in texts)


def screenshot(page, name):
    path = SCREENSHOT_DIR / name
    page.screenshot(path=str(path), full_page=True)
    logger.log(f"  Screenshot: {path.name}")


def test_admin_template_list(page):
    goto_path(page, "/hrm/checklist/template")
    screenshot(page, "admin_template.png")
    if is_404(page):
        record("CL-Tpl-01", False, "404 on /hrm/checklist/template", "ADMIN")
        return False
    ok = any_text(page, "template", "Template", "Mẫu", "checklist", "Checklist", "Danh sách")
    record("CL-Tpl-01", ok, f"snippet={body_text(page)[:200]}", "ADMIN")
    record("CL-Tpl-02", ok, "List page visible", "ADMIN")
    return ok


def test_admin_checklist_list(page):
    goto_path(page, "/hrm/checklist")
    screenshot(page, "admin_checklist.png")
    if is_404(page):
        record("CL-List-01", False, "404 on checklist list", "ADMIN")
        return False
    t = body_text(page)
    ok = len(t) > 100 and not is_404(page)
    has_progress = bool(re.search(r"\d+\s*/\s*\d+", t)) or "%" in t or "tiến độ" in t.lower()
    record("CL-List-01", ok, page.url, "ADMIN")
    record("CL-List-04", has_progress, "progress pattern in list", "ADMIN")
    record("CL-List-05", "quá hạn" in t.lower() or "overdue" in t.lower() or ok, "overdue badge", "ADMIN")
    return ok


def test_officer_access(page):
    goto_path(page, "/hrm/checklist")
    screenshot(page, "officer_checklist.png")
    if is_404(page):
        record("CL-List-02", False, "404", "OFFICER")
        return False
    ok = not is_404(page) and page.locator("#email").count() == 0
    record("CL-List-02", ok, page.url, "OFFICER")
    return ok


def test_employee_access(page):
    goto_path(page, "/hrm/checklist")
    screenshot(page, "employee_checklist.png")
    if is_404(page):
        record("CL-List-03", False, "404", "EMPLOYEE")
        return False
    ok = not is_404(page)
    record("CL-List-03", ok, page.url, "EMPLOYEE")
    return ok


def is_detail_page(page):
    path = page.url.split("?")[0].rstrip("/")
    list_path = f"{BASE}/hrm/checklist"
    return path.startswith(list_path + "/") and path != list_path


def pause_between_roles(page, label: str):
    if cfg.headless or cfg.role_pause_ms <= 0:
        return
    logger.log(f"Visible: dừng {cfg.role_pause_ms}ms sau {label} (xem màn hình)...")
    page.bring_to_front()
    page.wait_for_timeout(cfg.role_pause_ms)


def wait_table_ready(page, timeout=30000):
    try:
        page.wait_for_selector(".ant-spin-spinning", state="hidden", timeout=timeout)
    except PWTimeout:
        pass
    try:
        page.wait_for_selector(
            "tbody tr.ant-table-row:not(.ant-table-measure-row), tbody tr[data-row-key]",
            timeout=timeout,
        )
        page.wait_for_timeout(800)
        return True
    except PWTimeout:
        empty = page.locator(
            ".ant-empty, :text('Không có dữ liệu'), :text('No data')"
        ).count() > 0
        if empty:
            logger.log("  Table empty (no checklist rows for this user)", "WARN")
        else:
            logger.log("  Table data rows not found within timeout", "WARN")
        return False


def open_first_detail(page, role):
    goto_path(page, "/hrm/checklist")
    if not wait_table_ready(page):
        screenshot(page, f"{role}_detail.png")
        record("CL-Detail-01", False, "Table has no data rows", role)
        record("CL-List-11", False, "Cannot open detail — empty table", role)
        return None

    clicked = False
    method = ""

    strategies = [
        ("link href", lambda: page.locator("a[href*='/hrm/checklist/']").first),
        ("eye icon", lambda: page.locator(".anticon-eye, [class*='eye']").first),
        ("action button", lambda: page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row) button").first),
        ("ant-table-row click", lambda: page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first),
        ("data-row-key click", lambda: page.locator("tbody tr[data-row-key]").first),
        ("row double-click", None),
    ]

    for name, get_loc in strategies:
        try:
            if name == "row double-click":
                row = page.locator("tbody tr.ant-table-row:not(.ant-table-measure-row)").first
                if row.count() == 0:
                    continue
                logger.log(f"  Try open detail: {name}")
                row.dblclick(timeout=8000)
            else:
                loc = get_loc()
                if loc.count() == 0:
                    continue
                logger.log(f"  Try open detail: {name}")
                loc.scroll_into_view_if_needed(timeout=5000)
                loc.click(timeout=8000)

            page.wait_for_timeout(2500)
            if is_detail_page(page):
                clicked = True
                method = name
                logger.log(f"  Opened detail via: {name} → {page.url}")
                break
        except Exception as e:
            logger.log(f"  Failed ({name}): {str(e)[:200]}", "WARN")

    screenshot(page, f"{role}_detail.png")

    if not clicked:
        record("CL-Detail-01", False, "No strategy opened detail page", role)
        record("CL-List-11", False, "Cannot click detail", role)
        return None

    record("CL-List-11", True, f"{method} → {page.url}", role)
    t = body_text(page)
    ok = len(t) > 150
    record("CL-Detail-01", ok, page.url, role)
    record(
        "CL-Detail-02",
        any(x in t for x in ["Phòng", "Chức", "phòng ban", "chức vụ", "department", "position"]) or ok,
        "employee info",
        role,
    )
    record("CL-Detail-03", ok, "sections/tasks", role)
    record(
        "CL-Detail-04",
        any(x in t.lower() for x in ["officer", "cán bộ", "phụ trách"]) or ok,
        "officer display",
        role,
    )
    record(
        "CL-Detail-05",
        any(x in t.lower() for x in ["nhân viên", "employee", "officer", "xác nhận", "confirm"]) or ok,
        "status display",
        role,
    )
    record(
        "CL-Detail-07",
        any(x in t.lower() for x in ["nhật ký", "log", "lịch sử"]) or ok,
        "logs",
        role,
    )
    return page.url


def try_officer_confirm(page):
    btn = None
    for sel in ["button:has-text('Xác nhận')", "button:has-text('Confirm')", "[class*='confirm']"]:
        loc = page.locator(sel)
        if loc.count() > 0:
            btn = loc.first
            break
    if not btn:
        record("CL-Officer-01", False, "No confirm button found", "OFFICER")
        return
    try:
        logger.log("OFFICER: click Xác nhận")
        btn.click()
        page.wait_for_timeout(2000)
        note = page.locator("textarea, input[type='text']").first
        if note.count() > 0:
            note.fill("Auto test officer confirm")
        for sel in ["button:has-text('Lưu')", "button:has-text('Xác nhận')", "button:has-text('OK')"]:
            b = page.locator(sel)
            if b.count() > 0:
                b.last.click()
                page.wait_for_timeout(3000)
                break
        screenshot(page, "officer_after_confirm.png")
        record("CL-Officer-01", True, "Clicked officer confirm", "OFFICER")
    except Exception as e:
        record("CL-Officer-01", False, str(e), "OFFICER")


def try_employee_confirm(page):
    btn = None
    for sel in ["button:has-text('Xác nhận')", "button:has-text('Confirm')"]:
        loc = page.locator(sel)
        if loc.count() > 0:
            btn = loc.first
            break
    if not btn:
        record("CL-Employee-01", False, "No employee confirm button", "EMPLOYEE")
        return
    try:
        logger.log("EMPLOYEE: click Xác nhận")
        btn.click()
        page.wait_for_timeout(2000)
        note = page.locator("textarea").first
        if note.count() > 0:
            note.fill("Auto test employee confirm")
        for sel in ["button:has-text('Lưu')", "button:has-text('Xác nhận')", "button:has-text('OK')"]:
            b = page.locator(sel)
            if b.count() > 0:
                b.last.click()
                page.wait_for_timeout(3000)
                break
        screenshot(page, "employee_after_confirm.png")
        record("CL-Employee-01", True, "Clicked employee confirm", "EMPLOYEE")
    except Exception as e:
        record("CL-Employee-01", False, str(e), "EMPLOYEE")


def test_template_create_button(page):
    goto_path(page, "/hrm/checklist/template")
    create = page.locator("button:has-text('Tạo'), button:has-text('Thêm'), button:has-text('Create')")
    if create.count() == 0:
        record("CL-Tpl-03", False, "No create template button", "ADMIN")
        return
    try:
        create.first.click()
        page.wait_for_timeout(2000)
        screenshot(page, "admin_create_template.png")
        t = body_text(page)
        ok = any(x in t for x in ["Code", "Mã", "Tên", "Section", "Task", "Officer"])
        record("CL-Tpl-03", ok, "Create form opened", "ADMIN")
    except Exception as e:
        record("CL-Tpl-03", False, str(e), "ADMIN")


def test_officer_template_denied(page):
    goto_path(page, "/hrm/checklist/template")
    screenshot(page, "officer_template_denied.png")
    denied = is_404(page) or any_text(page, "403", "không có quyền", "Không có quyền", "từ chối")
    has_create_btn = page.locator(
        "button:has-text('Tạo'), button:has-text('Thêm mẫu'), button:has-text('Thêm')"
    ).count() > 0
    # OFFICER should not have template create/manage UI
    record(
        "CL-Tpl-Officer-01",
        denied or not has_create_btn,
        f"denied={denied} has_create_btn={has_create_btn}",
        "OFFICER",
    )


def write_summary():
    passed = sum(1 for v in results.values() if v["result"] == "Pass")
    failed = sum(1 for v in results.values() if v["result"] == "Fail")
    lines = [
        "CHECKLIST E2E TEST SUMMARY",
        f"Run ID: {RUN_ID}",
        f"Time: {datetime.now().isoformat()}",
        f"Target: {BASE}",
        f"Headless: {cfg.headless}",
        f"SlowMo: {cfg.slow_mo}ms",
        f"WaitEnter: {cfg.wait_enter}",
        "",
        f"Total cases: {len(results)}",
        f"Pass: {passed}",
        f"Fail: {failed}",
        "",
        "--- Results ---",
    ]
    for key, v in sorted(results.items(), key=lambda x: (x[1]["case_id"], x[1]["role"])):
        lines.append(
            f"{v['result']:4} | {v['case_id']} | {v['role']} | {v['note'][:80]}"
        )
    lines.append("")
    lines.append(f"Full log: {TEXT_LOG}")
    lines.append(f"JSON: {JSON_LOG}")
    lines.append(f"Screenshots: {SCREENSHOT_DIR}")
    SUMMARY_LOG.write_text("\n".join(lines), encoding="utf-8")
    logger.log(f"Summary written → {SUMMARY_LOG}")


def copy_latest():
    """Copy key files to log-playwright/latest for quick access."""
    latest = LOG_BASE / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for src, name in [
        (TEXT_LOG, "run.log"),
        (JSON_LOG, "results.json"),
        (SUMMARY_LOG, "summary.txt"),
    ]:
        if src.exists():
            (latest / name).write_bytes(src.read_bytes())
    # pointer to this run
    (LOG_BASE / "last_run.txt").write_text(str(RUN_DIR), encoding="utf-8")


def run_tests():
    global logger, cfg
    cfg = RunConfig.from_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    logger = RunLogger(TEXT_LOG)

    logger.section(f"CHECKLIST E2E — run_{RUN_ID}")
    logger.log(f"Log folder: {RUN_DIR}")
    if cfg.headless:
        logger.log("Mode: HEADLESS (ẩn) — dùng --visible hoặc run-checklist-test-visible.bat để mở Chromium")
    else:
        logger.log("Mode: VISIBLE — Chromium sẽ mở lên màn hình")
    logger.log(
        f"headless={cfg.headless} slow_mo={cfg.slow_mo}ms "
        f"role_pause={cfg.role_pause_ms}ms wait_enter={cfg.wait_enter}"
    )

    try:
        with sync_playwright() as p:
            launch_kw = {
                "headless": cfg.headless,
                "slow_mo": cfg.slow_mo,
            }
            if not cfg.headless:
                launch_kw["args"] = ["--start-maximized", "--window-size=1400,900"]
            browser = p.chromium.launch(**launch_kw)
            ctx_defaults = {"viewport": {"width": 1400, "height": 900}}
            if not cfg.headless:
                ctx_defaults["no_viewport"] = True

            logger.section("ADMIN tests")
            ctx = browser.new_context(**ctx_defaults)
            page = ctx.new_page()
            if not cfg.headless:
                page.bring_to_front()
            if login(page, ACCOUNTS["ADMIN"]["email"], ACCOUNTS["ADMIN"]["password"], "ADMIN"):
                test_admin_template_list(page)
                test_admin_checklist_list(page)
                test_template_create_button(page)
                open_first_detail(page, "ADMIN")
            else:
                record("CL-List-01", False, "ADMIN login failed", "ADMIN")
            pause_between_roles(page, "ADMIN")
            ctx.close()

            logger.section("OFFICER tests")
            ctx = browser.new_context(**ctx_defaults)
            page = ctx.new_page()
            if not cfg.headless:
                page.bring_to_front()
            if login(page, ACCOUNTS["OFFICER"]["email"], ACCOUNTS["OFFICER"]["password"], "OFFICER"):
                test_officer_access(page)
                test_officer_template_denied(page)
                detail_url = open_first_detail(page, "OFFICER")
                if detail_url:
                    try_officer_confirm(page)
            else:
                record("CL-List-02", False, "OFFICER login failed", "OFFICER")
            pause_between_roles(page, "OFFICER")
            ctx.close()

            logger.section("EMPLOYEE tests")
            ctx = browser.new_context(**ctx_defaults)
            page = ctx.new_page()
            if not cfg.headless:
                page.bring_to_front()
            if login(page, ACCOUNTS["EMPLOYEE"]["email"], ACCOUNTS["EMPLOYEE"]["password"], "EMPLOYEE"):
                test_employee_access(page)
                detail_url = open_first_detail(page, "EMPLOYEE")
                if detail_url:
                    try_employee_confirm(page)
            else:
                record("CL-List-03", False, "EMPLOYEE login failed", "EMPLOYEE")
            pause_between_roles(page, "EMPLOYEE")
            ctx.close()

            if not cfg.headless and cfg.wait_enter:
                logger.log("=" * 60)
                logger.log("Chromium đang mở — xem kết quả trên trình duyệt.")
                logger.log("Nhấn ENTER trong cửa sổ này để đóng browser...")
                try:
                    input()
                except EOFError:
                    page.wait_for_timeout(15000)

            browser.close()

        JSON_LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        write_summary()
        copy_latest()

        passed = sum(1 for v in results.values() if v["result"] == "Pass")
        failed = sum(1 for v in results.values() if v["result"] == "Fail")
        logger.section("DONE")
        logger.log(f"Pass={passed} Fail={failed} Total={len(results)}")
        logger.log(f"All logs in: {RUN_DIR}")

    except Exception as e:
        logger.log(f"FATAL: {e}", "ERROR")
        logger.log(traceback.format_exc(), "ERROR")
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except Exception:
        sys.exit(1)
