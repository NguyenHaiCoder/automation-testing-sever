# -*- coding: utf-8 -*-
"""Playwright job orchestration for explore / E2E runs."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from api.paths import CASES_SCRIPT, E2E_SCRIPT, EXPLORE_LOG_DIR, EXPLORE_SCRIPT, ROOT, WORKSPACE
from api.runtime import app_root, backend_executable, is_frozen

_lock = threading.Lock()
_proc: subprocess.Popen | None = None
_state: dict = {
    "running": False,
    "mode": None,
    "caseIds": [],
    "startedAt": None,
    "finishedAt": None,
    "pid": None,
    "exitCode": None,
    "message": "",
}


def _python() -> str:
    return sys.executable


def _read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def get_job_state() -> dict:
    _sync_job_from_process()
    with _lock:
        return dict(_state)


def _sync_job_from_process() -> None:
    """Đồng bộ state khi process đã thoát nhưng monitor chưa kịp cập nhật."""
    global _proc
    with _lock:
        if not _state.get("running"):
            return
        proc = _proc
        if proc is None:
            _state["running"] = False
            return
        code = proc.poll()
        if code is None:
            return
        message = "Hoan tat" if code == 0 else f"Thoat voi ma {code}"
        if _state.get("message", "").startswith("Dang chay"):
            _state["message"] = message
        _state.update(
            running=False,
            finishedAt=datetime.now().isoformat(timespec="seconds"),
            exitCode=code,
        )
        _proc = None


def _job_log_path(mode: str) -> Path:
    log_dir = ROOT / "log" / "jobs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return log_dir / f"{mode}_{stamp}.log"


def _set_state(**kwargs) -> None:
    with _lock:
        _state.update(kwargs)


def last_explore_run() -> dict | None:
    hint = EXPLORE_LOG_DIR / "last_run.txt"
    if not hint.exists():
        return None
    run_dir = Path(hint.read_text(encoding="utf-8").strip())
    summary = run_dir / "docs" / "summary.md"
    return {
        "runDir": str(run_dir),
        "summary": summary.read_text(encoding="utf-8")[:4000] if summary.exists() else "",
    }


def last_e2e_run() -> dict | None:
    hint = WORKSPACE / "log-playwright" / "last_run.txt"
    if not hint.exists():
        return None
    run_dir = Path(hint.read_text(encoding="utf-8").strip())
    results = run_dir / "results.json"
    summary = run_dir / "summary.txt"
    info: dict = {"runDir": str(run_dir)}
    if results.exists():
        raw = _read_json(results)
        if isinstance(raw, dict):
            info["passed"] = sum(1 for v in raw.values() if v.get("result") == "Pass")
            info["failed"] = sum(1 for v in raw.values() if v.get("result") == "Fail")
            info["total"] = len(raw)
    if summary.exists():
        info["summary"] = summary.read_text(encoding="utf-8")[:4000]
    return info


def get_status_payload() -> dict:
    return {
        "job": get_job_state(),
        "lastExplore": last_explore_run(),
        "lastE2E": last_e2e_run(),
    }


def _monitor(proc: subprocess.Popen, mode: str, log_handle) -> None:
    global _proc
    code = -1
    try:
        code = proc.wait()
        message = "Hoan tat" if code == 0 else f"Thoat voi ma {code}"
        if mode == "cases" and code == 0:
            message = f"Hoan tat {len(_state.get('caseIds') or [])} test case"
        _set_state(
            running=False,
            finishedAt=datetime.now().isoformat(timespec="seconds"),
            exitCode=code,
            message=message,
        )
    finally:
        try:
            log_handle.close()
        except Exception:
            pass
        with _lock:
            if _proc is proc:
                _proc = None


def _build_job_command(mode: str, visible: bool, case_ids: list[str] | None = None) -> tuple[list[str], str]:
    if is_frozen():
        exe = str(backend_executable())
        cwd = str(app_root())
        if mode == "explore":
            return [exe, "explore", "--visible" if visible else "--headless"], cwd
        if mode == "cases":
            ids = ",".join(case_ids or [])
            args = [exe, "cases", "--cases", ids]
            if visible:
                args.append("--visible")
            return args, cwd
        args = [exe, "run"]
        if visible:
            args.append("--visible")
        return args, cwd

    if mode == "explore":
        if not EXPLORE_SCRIPT.exists():
            raise FileNotFoundError(f"Khong tim thay script: {EXPLORE_SCRIPT}")
        return [_python(), str(EXPLORE_SCRIPT), "--visible" if visible else "--headless"], str(ROOT)

    if mode == "cases":
        if not CASES_SCRIPT.exists():
            raise FileNotFoundError(f"Khong tim thay script: {CASES_SCRIPT}")
        ids = ",".join(case_ids or [])
        args = [_python(), str(CASES_SCRIPT), "--cases", ids]
        if visible:
            args.append("--visible")
        return args, str(ROOT)

    if not E2E_SCRIPT.exists():
        raise FileNotFoundError(f"Khong tim thay script: {E2E_SCRIPT}")
    args = [_python(), str(E2E_SCRIPT)]
    if visible:
        args.append("--visible")
    return args, str(WORKSPACE)


def _kill_process_tree(pid: int) -> None:
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=False,
            capture_output=True,
            creationflags=flags,
        )
        return
    import os
    import signal

    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        os.kill(pid, signal.SIGTERM)


def stop_job() -> tuple[int, dict]:
    global _proc
    st = get_job_state()
    if not st["running"]:
        return 409, {"error": "Khong co tien trinh dang chay", "status": st}

    proc = _proc
    if proc is None or proc.poll() is not None:
        _set_state(
            running=False,
            finishedAt=datetime.now().isoformat(timespec="seconds"),
            exitCode=proc.returncode if proc else -1,
            message="Tien trinh da ket thuc",
        )
        _proc = None
        return 409, {"error": "Tien trinh da ket thuc"}

    pid = proc.pid
    try:
        _kill_process_tree(pid)
    except Exception as exc:  # noqa: BLE001
        return 500, {"error": f"Khong cham dut duoc: {exc}"}

    _set_state(
        running=False,
        finishedAt=datetime.now().isoformat(timespec="seconds"),
        exitCode=-1,
        message="Da cham dut boi nguoi dung",
    )
    _proc = None
    return 200, {"ok": True, "message": "Da cham dut tien trinh", "pid": pid}


def start_job(mode: str, visible: bool) -> tuple[int, dict]:
    return _start_process(mode, visible, case_ids=None)


def start_cases_job(case_ids: list[str], visible: bool) -> tuple[int, dict]:
    cleaned = [cid.strip() for cid in case_ids if cid and str(cid).strip()]
    if not cleaned:
        return 400, {"error": "Thieu danh sach caseIds"}
    return _start_process("cases", visible, case_ids=cleaned)


def _start_process(mode: str, visible: bool, case_ids: list[str] | None) -> tuple[int, dict]:
    global _proc
    st = get_job_state()
    if st["running"]:
        return 409, {"error": "Dang co tien trinh chay", "status": st}

    try:
        args, cwd = _build_job_command(mode, visible, case_ids)
    except FileNotFoundError as exc:
        return 404, {"error": str(exc)}

    log_path = _job_log_path(mode)
    log_handle = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        args,
        cwd=str(cwd),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    _proc = proc
    if mode == "cases":
        n = len(case_ids or [])
        run_message = f"Dang chay {n} test case tren 1 Chromium..."
        label = f"Chay {n} test case"
    elif mode == "explore":
        run_message = "Dang chay kham pha UI..."
        label = "Kham pha"
    else:
        run_message = "Dang chay kiem thu E2E..."
        label = "Bat dau kiem thu"
    _set_state(
        running=True,
        mode=mode,
        caseIds=list(case_ids or []),
        startedAt=datetime.now().isoformat(timespec="seconds"),
        finishedAt=None,
        pid=proc.pid,
        exitCode=None,
        message=run_message,
    )
    threading.Thread(target=_monitor, args=(proc, mode, log_handle), daemon=True).start()
    return 202, {
        "ok": True,
        "message": f"{label} — Chromium {'hien thi' if visible else 'headless'}",
        "pid": proc.pid,
        "logFile": str(log_path),
        "caseIds": list(case_ids or []),
    }
