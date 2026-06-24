# -*- coding: utf-8 -*-
"""Helper tên template automationtestver{N} — đồng bộ toàn hệ thống từ ver11."""
from __future__ import annotations

from pathlib import Path

from workflow.ADMIN.tpl_constants import AUTOMATION_TEMPLATE_VERSION_MIN
from workflow.common import WorkflowContext

TPL02_MARKER = "_tpl02_created.txt"
TPL07_MARKER = "_tpl07_edited.txt"


def _version_state_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "automation_template_next.txt"


def peek_next_template_version() -> int:
    path = _version_state_path()
    if not path.is_file():
        return AUTOMATION_TEMPLATE_VERSION_MIN
    try:
        return max(int(path.read_text(encoding="utf-8").strip()), AUTOMATION_TEMPLATE_VERSION_MIN)
    except ValueError:
        return AUTOMATION_TEMPLATE_VERSION_MIN


def allocate_next_template_version() -> int:
    """Cấp phát N tiếp theo và lưu N+1 vào data/automation_template_next.txt."""
    n = peek_next_template_version()
    path = _version_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(n + 1), encoding="utf-8")
    return n


def next_template_name(case: dict | None = None) -> str:
    del case  # dùng bộ đếm global, không phụ thuộc evidenceRuns từng case
    return f"automationtestver{allocate_next_template_version()}"


def last_allocated_template_name() -> str | None:
    last = peek_next_template_version() - 1
    if last < AUTOMATION_TEMPLATE_VERSION_MIN:
        return None
    return f"automationtestver{last}"


def remember_tpl02_created(ctx: WorkflowContext, template_name: str) -> None:
    marker = ctx.run_dir.parent / TPL02_MARKER
    marker.write_text(template_name.strip(), encoding="utf-8")


def resolve_tpl02_template_name(ctx: WorkflowContext) -> str | None:
    """Tên template ADM-TPL-02 vừa tạo — ưu tiên marker cùng session, rồi bộ đếm global."""
    marker = ctx.run_dir.parent / TPL02_MARKER
    if marker.is_file():
        name = marker.read_text(encoding="utf-8").strip()
        if name:
            return name
    return last_allocated_template_name()


def remember_tpl07_edited(ctx: WorkflowContext, template_name: str) -> None:
    marker = ctx.run_dir.parent / TPL07_MARKER
    marker.write_text(template_name.strip(), encoding="utf-8")


def resolve_tpl07_edited_name(ctx: WorkflowContext) -> str | None:
    """Tên template sau ADM-TPL-07 — ưu tiên marker cùng session."""
    marker = ctx.run_dir.parent / TPL07_MARKER
    if marker.is_file():
        name = marker.read_text(encoding="utf-8").strip()
        if name:
            return name
    return last_allocated_template_name()
