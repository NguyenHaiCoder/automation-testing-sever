# -*- coding: utf-8 -*-
"""List, read, and serve automation log runs (grouped by role)."""
from __future__ import annotations

import mimetypes
import os
import re
from datetime import datetime
from pathlib import Path

from api.paths import E2E_LOG_DIR, EXPLORE_LOG_DIR, CASE_RUNS_DIR, ROOT

ROLES = ("ADMIN", "OFFICER", "EMPLOYEE")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
ROLE_LOG_RE = re.compile(r"\[(ADMIN|OFFICER|EMPLOYEE)\]")


def _validate_run_dir(base: Path) -> None:
    allowed_roots = [
        EXPLORE_LOG_DIR.resolve(),
        E2E_LOG_DIR.resolve(),
        CASE_RUNS_DIR.resolve(),
    ]
    resolved = base.resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise FileNotFoundError("Log run not found")
    if not any(str(resolved).startswith(str(root)) for root in allowed_roots):
        raise PermissionError("Path not allowed")


def find_run_dir(run_id: str) -> Path | None:
    for root in (CASE_RUNS_DIR, EXPLORE_LOG_DIR, E2E_LOG_DIR):
        candidate = root / run_id
        if candidate.is_dir():
            return candidate
    return None


def _detect_role_from_rel(rel: str) -> str | None:
    norm = rel.replace("\\", "/")
    parts = norm.split("/")
    if len(parts) >= 2 and parts[0] == "picture" and parts[1] in ROLES:
        return parts[1]
    if parts[0] == "json" or (len(parts) >= 2 and parts[-2] == "json"):
        name = parts[-1] if parts[0] == "json" else parts[-1]
        for role in ROLES:
            if name.upper().startswith(f"{role}_") or name.upper().startswith(role):
                return role
    if "screenshots" in parts:
        name = parts[-1]
        for role in ROLES:
            if f"_{role.lower()}" in name.lower() or f"-{role.lower()}" in name.lower():
                return role
    return None


def _file_kind(rel: str) -> str:
    ext = Path(rel).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext == ".json":
        return "json"
    if ext == ".log":
        return "log"
    if ext in {".md", ".txt"}:
        return "text"
    return "other"


def _make_file_entry(base: Path, rel: str) -> dict:
    fp = base / rel
    role = _detect_role_from_rel(rel)
    return {
        "name": rel,
        "rel": rel,
        "size": fp.stat().st_size,
        "role": role,
        "kind": _file_kind(rel),
        "runId": base.name,
    }


def _split_log_by_role(log_text: str) -> dict[str, str]:
    buckets: dict[str, list[str]] = {role: [] for role in ROLES}
    shared: list[str] = []
    for line in log_text.splitlines():
        match = ROLE_LOG_RE.search(line)
        if match and match.group(1) in buckets:
            buckets[match.group(1)].append(line)
        else:
            shared.append(line)
    shared_text = "\n".join(shared)
    result = {role: "\n".join(buckets[role]) for role in ROLES if buckets[role]}
    if shared_text:
        result["SHARED"] = shared_text
    return result


def _group_files_by_role(files: list[dict]) -> list[dict]:
    groups: dict[str, dict] = {
        role: {"role": role, "pictures": [], "jsonFiles": [], "others": [], "logTail": ""}
        for role in ROLES
    }
    unassigned: list[dict] = []

    for f in files:
        role = f.get("role")
        kind = f.get("kind")
        if role in groups:
            if kind == "image":
                groups[role]["pictures"].append(f)
            elif kind == "json":
                groups[role]["jsonFiles"].append(f)
            else:
                groups[role]["others"].append(f)
        else:
            unassigned.append(f)

    bundles = []
    for role in ROLES:
        g = groups[role]
        if g["pictures"] or g["jsonFiles"] or g["others"]:
            bundles.append(g)

    if unassigned:
        bundles.append({"role": "OTHER", "pictures": [], "jsonFiles": [], "others": unassigned, "logTail": ""})

    return bundles


def _run_info(run_dir: Path, run_type: str) -> dict:
    stat = run_dir.stat()
    info: dict = {
        "id": run_dir.name,
        "type": run_type,
        "path": str(run_dir),
        "createdAt": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "mtime": stat.st_mtime,
    }
    if run_type == "explore":
        summary = run_dir / "docs" / "summary.md"
        log_file = run_dir / "log" / "explore.log"
        json_dir = run_dir / "json"
        picture_dir = run_dir / "picture"
        info["summaryFile"] = str(summary) if summary.exists() else ""
        info["logFile"] = str(log_file) if log_file.exists() else ""
        info["jsonCount"] = len(list(json_dir.glob("*.json"))) if json_dir.exists() else 0
        info["pictureCount"] = sum(1 for _ in picture_dir.rglob("*") if _.suffix.lower() in IMAGE_EXTS) if picture_dir.exists() else 0
        info["picturesByRole"] = {}
        if picture_dir.exists():
            for role in ROLES:
                role_dir = picture_dir / role
                if role_dir.is_dir():
                    info["picturesByRole"][role] = sum(
                        1 for _ in role_dir.glob("*") if _.suffix.lower() in IMAGE_EXTS
                    )
    elif run_type == "case-run":
        results = run_dir / "results.json"
        info["resultsFile"] = str(results) if results.exists() else ""
        info["pictureCount"] = sum(
            1 for _ in run_dir.rglob("*.png") if _.suffix.lower() in IMAGE_EXTS
        )
        info["picturesByRole"] = {}
    else:
        summary = run_dir / "summary.txt"
        results = run_dir / "results.json"
        log_file = run_dir / "run.log"
        shots = run_dir / "screenshots"
        info["summaryFile"] = str(summary) if summary.exists() else ""
        info["logFile"] = str(log_file) if log_file.exists() else ""
        info["resultsFile"] = str(results) if results.exists() else ""
        info["pictureCount"] = len(list(shots.glob("*.png"))) if shots.exists() else 0
        info["picturesByRole"] = {}
    return info


def list_log_runs() -> list[dict]:
    runs: list[dict] = []
    if CASE_RUNS_DIR.exists():
        for run_dir in CASE_RUNS_DIR.glob("run_*"):
            if run_dir.is_dir():
                runs.append(_run_info(run_dir, "case-run"))
    if EXPLORE_LOG_DIR.exists():
        for run_dir in EXPLORE_LOG_DIR.glob("run_*"):
            if run_dir.is_dir():
                runs.append(_run_info(run_dir, "explore"))
    if E2E_LOG_DIR.exists():
        for run_dir in E2E_LOG_DIR.glob("run_*"):
            if run_dir.is_dir():
                runs.append(_run_info(run_dir, "e2e"))
    runs.sort(key=lambda r: r["mtime"], reverse=True)
    return runs


def read_log_detail(run_path: str, tail_lines: int = 300) -> dict:
    base = Path(run_path).resolve()
    _validate_run_dir(base)
    return _build_detail(base, tail_lines)


def read_log_detail_by_id(run_id: str, tail_lines: int = 300) -> dict:
    base = find_run_dir(run_id)
    if base is None:
        raise FileNotFoundError("Log run not found")
    return _build_detail(base, tail_lines)


def _build_detail(base: Path, tail_lines: int) -> dict:
    if str(base).startswith(str(CASE_RUNS_DIR.resolve())):
        run_type = "case-run"
    elif str(base).startswith(str(EXPLORE_LOG_DIR.resolve())):
        run_type = "explore"
    else:
        run_type = "e2e"
    info = _run_info(base, run_type)

    def read_tail(path: Path) -> str:
        if not path.exists():
            return ""
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-tail_lines:])

    files: list[dict] = []
    for root, _dirs, filenames in os.walk(base):
        for name in filenames:
            fp = Path(root) / name
            rel = fp.relative_to(base).as_posix()
            files.append(_make_file_entry(base, rel))

    files.sort(key=lambda f: f["name"])

    summary_text = ""
    if info.get("summaryFile"):
        summary_text = Path(info["summaryFile"]).read_text(encoding="utf-8", errors="replace")[:12000]

    full_log = ""
    if info.get("logFile"):
        full_log = read_tail(Path(info["logFile"]))

    log_by_role = _split_log_by_role(full_log)
    role_bundles = _group_files_by_role(files)
    for bundle in role_bundles:
        role = bundle["role"]
        if role in log_by_role:
            bundle["logTail"] = log_by_role[role]
    if log_by_role.get("SHARED"):
        shared_bundle = next((b for b in role_bundles if b["role"] == "OTHER"), None)
        if shared_bundle:
            shared_bundle["logTail"] = log_by_role["SHARED"]
        elif role_bundles:
            role_bundles[0]["logTail"] = (
                role_bundles[0].get("logTail", "") + "\n" + log_by_role["SHARED"]
            ).strip()

    return {
        **info,
        "summary": summary_text,
        "logTail": full_log,
        "logByRole": log_by_role,
        "roles": role_bundles,
        "files": files,
    }


def resolve_run_file(run_path: str | None, run_id: str | None, rel: str) -> Path:
    if not rel or ".." in rel.replace("\\", "/"):
        raise PermissionError("Invalid file path")

    norm_rel = rel.replace("\\", "/").lstrip("/")
    if run_id:
        base = find_run_dir(run_id)
        if base is None:
            raise FileNotFoundError("Log run not found")
    elif run_path:
        base = Path(run_path).resolve()
        _validate_run_dir(base)
    else:
        raise ValueError("Missing runId or path")

    _validate_run_dir(base)
    target = (base / norm_rel).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise PermissionError("Path not allowed")
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("File not found")
    return target


def read_file_bytes(path: Path) -> tuple[bytes, str]:
    mime, _ = mimetypes.guess_type(str(path))
    return path.read_bytes(), mime or "application/octet-stream"
