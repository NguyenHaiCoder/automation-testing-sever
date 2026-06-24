# -*- coding: utf-8 -*-
"""Runtime paths for dev vs PyInstaller frozen exe."""
from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def bundle_root() -> Path:
    """Read-only bundled resources (_MEIPASS when frozen)."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[1]


def app_root() -> Path:
    """Writable application root (logs, data) — folder containing exe when packaged."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def workspace_root() -> Path:
    """Project workspace (Excel, log-playwright) — bundled next to exe when packaged."""
    if is_frozen():
        return app_root()
    return app_root().parent


def backend_executable() -> Path:
    return Path(sys.executable).resolve()
