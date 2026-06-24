# -*- coding: utf-8 -*-
"""
Chạy các test case đã chọn — một phiên Chromium, lần lượt từng case.

Dev:
  cd MAIN_AUTOMATION_TEST
  python run_test_cases.py --cases BR-TPL-01 --visible
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JSON = ROOT / "data" / "testcases.json"
RUN_LOG_DIR = ROOT / "log" / "case-runs"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def load_cases(case_ids: list[str]) -> list[dict]:
    if not DATA_JSON.exists():
        print(f"[ERROR] Khong tim thay {DATA_JSON}")
        sys.exit(2)
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in data.get("cases", [])}
    missing = [cid for cid in case_ids if cid not in by_id]
    if missing:
        print(f"[ERROR] Khong tim thay case: {', '.join(missing)}")
        sys.exit(2)
    return [by_id[cid] for cid in case_ids]


def run_cases(case_ids: list[str], visible: bool) -> int:
    from playwright.sync_api import sync_playwright

    from config.settings import Settings
    from workflow.runner import has_workflow, run_workflow

    cases = load_cases(case_ids)
    settings = Settings.load()
    headless = not visible
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = RUN_LOG_DIR / f"run_{run_id}"
    session_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}

    print(f"[CASES] {len(cases)} case — 1 Chromium session ({'headless' if headless else 'visible'})")
    print(f"[CASES] Log: {session_dir}")
    for tc in cases:
        desc = (tc.get("description") or "")[:70]
        print(f"  · {tc['id']}: {desc}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            slow_mo=400 if not headless else 0,
        )
        context = browser.new_context()
        page = context.new_page()
        if not headless:
            page.bring_to_front()
        try:
            for index, tc in enumerate(cases, start=1):
                cid = tc["id"]
                case_dir = session_dir / cid
                case_dir.mkdir(parents=True, exist_ok=True)
                print(f"\n[CASE {index}/{len(cases)}] === {cid} ===")
                print(f"[CASE] Mo ta: {tc.get('description', '')}")

                if has_workflow(cid):
                    try:
                        outcome = run_workflow(tc, page, settings, case_dir)
                    except Exception as exc:  # noqa: BLE001
                        err_shot = case_dir / f"{cid}_error.png"
                        try:
                            page.screenshot(path=str(err_shot), full_page=True)
                        except Exception:
                            pass
                        outcome = {"result": "Fail", "message": str(exc)}
                    result = outcome.get("result", "Untested")
                    print(f"[CASE] Ket qua: {result} — {outcome.get('message', '')}")
                    results[cid] = outcome
                else:
                    print("[CASE] Stub — chua co workflow, bo qua")
                    results[cid] = {"result": "Untested", "message": "Chua co workflow"}
                    page.wait_for_timeout(300)
        finally:
            context.close()
            browser.close()

    summary_path = session_dir / "results.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        from api.services.case_result_sync import apply_case_results

        apply_case_results(session_dir, results)
        print("[CASES] Da cap nhat ket qua + minh chung vao testcases.json")
    except Exception as exc:  # noqa: BLE001
        print(f"[CASES] Canh bao: khong ghi duoc testcases.json — {exc}")

    failed = sum(1 for r in results.values() if r.get("result") == "Fail")
    print(f"\n[CASES] Hoan tat — Fail: {failed}/{len(results)}")
    return 1 if failed else 0


def main() -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(description="Run selected checklist test cases")
    parser.add_argument("--cases", required=True, help="Danh sach ID, phan cach bang dau phay")
    parser.add_argument("--visible", "-v", action="store_true", help="Hien Chromium")
    parser.add_argument("--headless", action="store_true", help="Chay an")
    args = parser.parse_args()

    case_ids = [x.strip() for x in args.cases.split(",") if x.strip()]
    if not case_ids:
        print("[ERROR] Thieu case ID")
        return 1

    visible = args.visible and not args.headless
    return run_cases(case_ids, visible)


if __name__ == "__main__":
    sys.exit(main())
