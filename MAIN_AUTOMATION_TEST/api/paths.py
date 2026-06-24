# -*- coding: utf-8 -*-
"""Central path configuration for MAIN_AUTOMATION_TEST."""
from __future__ import annotations

import os
from pathlib import Path

from api.runtime import app_root, bundle_root, workspace_root

ROOT = app_root()
WORKSPACE = workspace_root()
_BUNDLE = bundle_root()

DATA_DIR = ROOT / "data"
DATA_JSON = DATA_DIR / "testcases.json"
EXCEL_PATH = WORKSPACE / "2. IT_TestCase-Checklist-Cursor.xlsx"
EXPLORE_SCRIPT = ROOT / "explore_checklist.py"
CASES_SCRIPT = ROOT / "run_test_cases.py"
E2E_SCRIPT = WORKSPACE / "run_checklist_e2e.py"
SYNC_SCRIPT = WORKSPACE / "sync_results_to_excel.py"
EXPLORE_LOG_DIR = ROOT / "log"
CASE_RUNS_DIR = ROOT / "log" / "case-runs"
E2E_LOG_DIR = WORKSPACE / "log-playwright"
ACCOUNTS_ENV = ROOT / "accounts.env"

_default_fe = ROOT.parent / "MAIN_AUTOMATION_TEST_FE" / "dist"
FE_DIST = Path(os.environ.get("FE_DIST", str(_default_fe))).resolve()

API_HOST = os.environ.get("API_HOST", "127.0.0.1")
# Render/Railway set PORT; local dev uses API_PORT (default 8765)
API_PORT = int(os.environ.get("PORT", os.environ.get("API_PORT", "8765")))

ADMIN_CONTACT_MESSAGE = "Vui lòng liên hệ admin"


def is_admin_restricted() -> bool:
    return os.environ.get("RESTRICT_ADMIN", "").strip().lower() in ("1", "true", "yes", "on")


_ACCOUNT_ENV_KEYS = (
    "BASE_URL",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
    "ADMIN_ROLE",
    "ADMIN_NOTE",
    "OFFICER_EMAIL",
    "OFFICER_PASSWORD",
    "OFFICER_ROLE",
    "OFFICER_NOTE",
    "EMPLOYEE_EMAIL",
    "EMPLOYEE_PASSWORD",
    "EMPLOYEE_ROLE",
    "EMPLOYEE_NOTE",
    "HEADLESS",
    "SLOW_MO",
    "PARALLEL_BROWSERS",
)


def sync_accounts_env_from_environ() -> None:
    """Render: tạo accounts.env từ biến môi trường dashboard nếu chưa có file."""
    if ACCOUNTS_ENV.exists():
        return
    if not os.environ.get("ADMIN_EMAIL"):
        return
    lines = ["# Auto-generated from environment (Render/deploy)\n"]
    for key in _ACCOUNT_ENV_KEYS:
        val = os.environ.get(key)
        if val is not None and val != "":
            lines.append(f"{key}={val}\n")
    ACCOUNTS_ENV.write_text("".join(lines), encoding="utf-8")


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPLORE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    E2E_LOG_DIR.mkdir(parents=True, exist_ok=True)

    sync_accounts_env_from_environ()

    bundled_data = _BUNDLE / "data" / "testcases.json"
    if not DATA_JSON.exists() and bundled_data.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DATA_JSON.write_bytes(bundled_data.read_bytes())

    bundled_accounts = _BUNDLE / "accounts.env"
    if not ACCOUNTS_ENV.exists() and bundled_accounts.exists():
        ACCOUNTS_ENV.write_bytes(bundled_accounts.read_bytes())
