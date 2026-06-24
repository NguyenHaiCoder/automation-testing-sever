# -*- coding: utf-8 -*-
"""Shared helpers for workflow automation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from config.settings import Settings


@dataclass
class WorkflowContext:
    page: Page
    settings: Settings
    case: dict
    run_dir: Path
    role: str = "ADMIN"
    log_lines: list[str] = field(default_factory=list)

    def log(self, msg: str, level: str = "INFO") -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}"
        self.log_lines.append(line)
        print(line, flush=True)

    def admin_account(self):
        for acc in self.settings.accounts:
            if acc.role == self.role:
                return acc
        raise RuntimeError(f"Khong tim thay tai khoan {self.role}")

    def login_admin(self) -> None:
        self.login_as("ADMIN")

    def login_as(self, role: str) -> None:
        from workflow.helpers.checklist_ui import login_as as _login

        _login(self, role)

    def screenshot(self, name: str) -> Path:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        path = self.run_dir / f"{self.case.get('id', 'case')}_{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        self.log(f"Screenshot → {path.name}")
        return path

    def goto(self, path: str) -> None:
        url = self.settings.base_url.rstrip("/") + path
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(1500)
