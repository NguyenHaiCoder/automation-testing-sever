# -*- coding: utf-8 -*-
"""
HTTP API server for React dashboard.

Run:
  cd MAIN_AUTOMATION_TEST
  python -m api

Endpoints:
  GET  /api/testcases
  PUT  /api/testcases
  GET  /api/logs
  GET  /api/logs/detail?path=... | ?runId=...
  GET  /api/logs/file?runId=...&rel=picture/ADMIN/foo.png
  GET  /api/status
  POST /api/explore
  POST /api/run
  POST /api/run-cases
  POST /api/stop
"""
from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from api.paths import (
    ADMIN_CONTACT_MESSAGE,
    API_HOST,
    API_PORT,
    DATA_JSON,
    FE_DIST,
    ROOT,
    WORKSPACE,
    ensure_runtime_dirs,
    is_admin_restricted,
)
from api.services.job_runner import get_status_payload, start_cases_job, start_job, stop_job
from api.services.log_manager import (
    list_log_runs,
    read_file_bytes,
    read_log_detail,
    read_log_detail_by_id,
    resolve_run_file,
)
from api.services.testcase_store import load_testcases_json, save_testcases


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        safe = msg.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        )
        print(safe, flush=True)


_configure_stdio()


def _admin_denied() -> dict:
    return {"error": ADMIN_CONTACT_MESSAGE}


class ApiHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        _log(f"[API] {self.address_string()} - {fmt % args}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, code: int, data: bytes, content_type: str, *, cache: str = "private, max-age=3600") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, code: int, data: bytes, content_type: str) -> None:
        self._send_bytes(code, data, content_type)

    def _resolve_static(self, url_path: str) -> Path | None:
        if not FE_DIST.is_dir():
            return None
        rel = unquote(url_path.lstrip("/")) or "index.html"
        candidate = (FE_DIST / rel).resolve()
        try:
            candidate.relative_to(FE_DIST.resolve())
        except ValueError:
            return None
        if candidate.is_file():
            return candidate
        index = FE_DIST / "index.html"
        return index if index.is_file() else None

    def _try_serve_static(self, url_path: str) -> bool:
        fp = self._resolve_static(url_path)
        if fp is None:
            return False
        mime, _ = mimetypes.guess_type(str(fp))
        cache = "public, max-age=31536000, immutable" if "/assets/" in fp.as_posix() else "no-cache"
        self._send_bytes(200, fp.read_bytes(), mime or "application/octet-stream", cache=cache)
        return True

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        from urllib.parse import parse_qs

        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/api/health":
            from api.runtime import is_frozen

            self._send(
                200,
                {
                    "ok": True,
                    "frozen": is_frozen(),
                    "restrictAdmin": is_admin_restricted(),
                    "feDist": FE_DIST.is_dir(),
                },
            )
            return

        if parsed.path == "/api/testcases":
            if qs.get("refresh", ["0"])[0] in ("1", "true"):
                self._send(
                    410,
                    {
                        "error": "Import Excel da ngung — chi dung data/testcases.json (v2). "
                        "Chay: python scripts/generate_testcases_v2.py",
                    },
                )
                return
            data = load_testcases_json()
            if data is None:
                self._send(
                    404,
                    {
                        "error": f"Khong tim thay {DATA_JSON.name}. "
                        "Chay: python scripts/generate_testcases_v2.py",
                    },
                )
                return
            self._send(200, data)
            return

        if parsed.path == "/api/logs":
            if is_admin_restricted():
                self._send(403, _admin_denied())
                return
            try:
                runs = list_log_runs()
                self._send(200, {"runs": runs, "total": len(runs)})
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": str(exc)})
            return

        if parsed.path == "/api/logs/detail":
            if is_admin_restricted():
                self._send(403, _admin_denied())
                return
            run_path = qs.get("path", [""])[0]
            run_id = qs.get("runId", [""])[0]
            if not run_path and not run_id:
                self._send(400, {"error": "Thieu tham so path hoac runId"})
                return
            try:
                detail = read_log_detail_by_id(run_id) if run_id else read_log_detail(run_path)
                self._send(200, detail)
            except FileNotFoundError:
                self._send(404, {"error": "Khong tim thay log run"})
            except PermissionError:
                self._send(403, {"error": "Khong duoc phep truy cap"})
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": str(exc)})
            return

        if parsed.path == "/api/logs/file":
            if is_admin_restricted():
                self._send(403, _admin_denied())
                return
            run_path = qs.get("path", [""])[0]
            run_id = qs.get("runId", [""])[0]
            rel = qs.get("rel", [""])[0]
            if not rel:
                self._send(400, {"error": "Thieu tham so rel"})
                return
            try:
                fp = resolve_run_file(run_path or None, run_id or None, rel)
                data, mime = read_file_bytes(fp)
                self._send_file(200, data, mime)
            except FileNotFoundError:
                self._send(404, {"error": "Khong tim thay file"})
            except PermissionError:
                self._send(403, {"error": "Khong duoc phep truy cap"})
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": str(exc)})
            return

        if parsed.path == "/api/status":
            self._send(200, get_status_payload())
            return

        if self._try_serve_static(parsed.path):
            return

        self._send(404, {"error": "Not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        body = self._read_body()
        visible = bool(body.get("visible", True))

        if parsed.path == "/api/explore":
            code, payload = start_job("explore", visible)
            self._send(code, payload)
            return

        if parsed.path == "/api/run":
            code, payload = start_job("run", visible)
            self._send(code, payload)
            return

        if parsed.path == "/api/run-cases":
            case_ids = body.get("caseIds") or body.get("cases") or []
            if isinstance(case_ids, str):
                case_ids = [x.strip() for x in case_ids.split(",") if x.strip()]
            code, payload = start_cases_job(case_ids, visible)
            self._send(code, payload)
            return

        if parsed.path == "/api/stop":
            code, payload = stop_job()
            self._send(code, payload)
            return

        self._send(404, {"error": "Not found"})

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/testcases":
            if is_admin_restricted():
                self._send(403, _admin_denied())
                return
            if not body.get("cases"):
                self._send(400, {"error": "Payload khong hop le — thieu cases"})
                return
            try:
                saved = save_testcases(body)
                self._send(200, {"ok": True, "message": "Da luu testcases.json", "data": saved})
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": str(exc)})
            return

        self._send(404, {"error": "Not found"})


def main() -> None:
    ensure_runtime_dirs()
    _log(f"[API] ROOT: {ROOT}")
    _log(f"[API] WORKSPACE: {WORKSPACE}")
    if FE_DIST.is_dir():
        _log(f"[API] Serving FE static: {FE_DIST}")
    if is_admin_restricted():
        _log(f"[API] RESTRICT_ADMIN=on — log & testcase edit blocked")
    _log(f"[API] Listening on http://{API_HOST}:{API_PORT}")
    server = HTTPServer((API_HOST, API_PORT), ApiHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log("\n[API] Stopped")


if __name__ == "__main__":
    main()
