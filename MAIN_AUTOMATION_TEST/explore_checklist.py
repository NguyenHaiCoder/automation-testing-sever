# -*- coding: utf-8 -*-
"""
Bước 1 — Explore Checklist UI (3 Chromium song song).

Đọc accounts.env → login ADMIN / OFFICER / EMPLOYEE đồng thời
→ explore màn /hrm/checklist, /hrm/checklist/template, chi tiết instance
→ log tables, buttons (clickable / not), links

Log: MAIN_AUTOMATION_TEST/log/run_DD-MM-YYYY_HH-MM-SS/
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config.settings import LOG_DIR, Settings, CHECKLIST_ROUTES  # noqa: E402
from src.logger_util import RunLogger, new_run_dir  # noqa: E402
from src.page_explorer import explore_role  # noqa: E402


def routes_for_role(role: str) -> list[dict]:
    return [r for r in CHECKLIST_ROUTES if role in r.get("roles", [])]


def build_summary(reports: list[dict], run_id: str) -> str:
    lines = [
        "# Checklist UI Explore Summary",
        f"Run ID: {run_id}",
        "",
    ]
    for rep in reports:
        role = rep["role"]
        lines.append(f"## {role} ({rep['email']})")
        lines.append(f"- Login: {'OK' if rep['login_ok'] else 'FAIL'}")
        if rep.get("errors"):
            lines.append(f"- Errors: {', '.join(rep['errors'])}")
        for deep in rep.get("deep_explores", []):
            lines.append(f"- **{deep.get('page_name')}** interactions={deep.get('interaction_count', 0)}")
            for act in deep.get("interactions", []):
                ss = act.get("screenshot", "")
                lines.append(f"  - `{act.get('action')}` → {ss or 'no shot'}")
        for pg in rep.get("pages", []):
            btns = pg.get("buttons", [])
            clickable = sum(1 for b in btns if b.get("category") == "clickable")
            not_click = sum(1 for b in btns if b.get("category") == "not_clickable")
            tbl_rows = sum(t.get("rowCount", 0) for t in pg.get("tables", []))
            lines.append(
                f"- **{pg.get('page_name')}** `{pg.get('url')}` "
                f"| tables rows={tbl_rows} | buttons clickable={clickable} disabled/hidden={not_click}"
            )
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Explore Checklist UI — 3 browsers parallel")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn (mặc định: hiện browser)")
    parser.add_argument("--visible", "-v", action="store_true", help="Hiện Chromium (mặc định)")
    args = parser.parse_args()

    settings = Settings.load()
    if args.headless:
        settings.headless = True
    elif args.visible:
        settings.headless = False
    else:
        # accounts.env HEADLESS=0 → visible by default for explore
        pass

    run_dir, run_id, layout = new_run_dir(LOG_DIR)

    logger = RunLogger(layout, "explore")
    logger.section(f"CHECKLIST EXPLORE — run_{run_id}")
    logger.log(f"Base URL: {settings.base_url}")
    logger.log(f"Parallel browsers: {len(settings.accounts)}")
    logger.log(f"Headless: {settings.headless} | SlowMo: {settings.slow_mo}ms")
    logger.log("Deep explore: search, filter, create, view, edit, row detail + screenshots")

    reports: list[dict] = []

    with ThreadPoolExecutor(max_workers=settings.parallel_browsers) as pool:
        futures = {
            pool.submit(
                explore_role,
                acc,
                settings,
                run_dir,
                layout,
                logger,
                routes_for_role(acc.role),
            ): acc.role
            for acc in settings.accounts
        }
        for fut in as_completed(futures):
            role = futures[fut]
            try:
                rep = fut.result()
                reports.append(rep)
                logger.save_json(f"{role}_explore.json", rep)
                logger.log(f"Done explore: {role}")
            except Exception as e:
                logger.log(f"Thread {role} failed: {e}", "ERROR")

    reports.sort(key=lambda r: {"ADMIN": 0, "OFFICER": 1, "EMPLOYEE": 2}.get(r["role"], 9))

    summary = build_summary(reports, run_id)
    logger.save_doc("summary.md", summary)

    total_pages = sum(len(r.get("pages", [])) for r in reports)
    total_tables = sum(
        len(p.get("tables", [])) for r in reports for p in r.get("pages", [])
    )
    logger.section("DONE")
    logger.log(f"Roles={len(reports)} pages_explored={total_pages} tables_found={total_tables}")
    logger.log(f"Run folder: {run_dir}")
    logger.log("  json/     — *.json")
    logger.log("  picture/ADMIN|OFFICER|EMPLOYEE  — *.png")
    logger.log("  log/      — *.log")
    logger.log("  docs/     — *.md")
    logger.close()


if __name__ == "__main__":
    main()
