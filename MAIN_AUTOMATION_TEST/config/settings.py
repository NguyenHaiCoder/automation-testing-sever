# -*- coding: utf-8 -*-
"""Cấu hình MAIN_AUTOMATION_TEST — load accounts.env."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from api.runtime import app_root as _app_root

    ROOT = _app_root()
except ImportError:
    pass

ENV_FILE = ROOT / "accounts.env"
LOG_DIR = ROOT / "log"
DOCS_DIR = ROOT / "docs"

# Màn hình FE theo checklist-ba.md §11 + menu sidebar liên quan
CHECKLIST_ROUTES = [
    {"path": "/hrm/checklist", "name": "Danh sách checklist", "roles": ["ADMIN", "OFFICER", "EMPLOYEE"]},
    {"path": "/hrm/checklist/template", "name": "Mẫu checklist (template)", "roles": ["ADMIN"]},
]

CHECKLIST_URL_PATTERNS = [
    "/hrm/checklist",
    "/hrm/checklist/template",
]


def load_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = value.strip()
    return data


@dataclass
class Account:
    role: str
    email: str
    password: str
    note: str = ""


@dataclass
class Settings:
    base_url: str
    accounts: list[Account]
    headless: bool
    slow_mo: int
    parallel_browsers: int
    routes: list[dict] = field(default_factory=lambda: list(CHECKLIST_ROUTES))

    @classmethod
    def load(cls) -> "Settings":
        env = load_env_file(ENV_FILE)
        # os.environ override
        for k, v in env.items():
            os.environ.setdefault(k, v)

        accounts = [
            Account(
                role="ADMIN",
                email=os.environ["ADMIN_EMAIL"],
                password=os.environ["ADMIN_PASSWORD"],
                note=os.environ.get("ADMIN_NOTE", ""),
            ),
            Account(
                role="OFFICER",
                email=os.environ["OFFICER_EMAIL"],
                password=os.environ["OFFICER_PASSWORD"],
                note=os.environ.get("OFFICER_NOTE", ""),
            ),
            Account(
                role="EMPLOYEE",
                email=os.environ["EMPLOYEE_EMAIL"],
                password=os.environ["EMPLOYEE_PASSWORD"],
                note=os.environ.get("EMPLOYEE_NOTE", ""),
            ),
        ]
        return cls(
            base_url=os.environ.get("BASE_URL", "https://qlrv.democloud.xyz").rstrip("/"),
            accounts=accounts,
            headless=os.environ.get("HEADLESS", "1") not in ("0", "false", "False"),
            slow_mo=int(os.environ.get("SLOW_MO", "0")),
            parallel_browsers=int(os.environ.get("PARALLEL_BROWSERS", "3")),
        )
