# -*- coding: utf-8 -*-
"""
Unified entry for packaged exe (PyInstaller).

  checklist-backend.exe           -> API server
  checklist-backend.exe api       -> API server
  checklist-backend.exe explore   -> UI explore (Playwright)
  checklist-backend.exe run       -> E2E tests
  checklist-backend.exe cases --cases ID1,ID2  -> selected test cases
"""
from __future__ import annotations

import sys
from pathlib import Path


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main() -> None:
    _configure_stdio()
    root = Path(__file__).resolve().parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    cmd = sys.argv[1] if len(sys.argv) > 1 else "api"

    if cmd == "api":
        from api.paths import ensure_runtime_dirs
        from api.server import main as api_main

        ensure_runtime_dirs()
        api_main()
        return

    if cmd == "explore":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        from explore_checklist import main as explore_main

        explore_main()
        return

    if cmd == "run":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        from api.runtime import bundle_root, workspace_root

        e2e = workspace_root() / "run_checklist_e2e.py"
        bundled = bundle_root() / "run_checklist_e2e.py"
        target = e2e if e2e.exists() else bundled
        if not target.exists():
            print(f"[ERROR] Khong tim thay run_checklist_e2e.py")
            sys.exit(1)
        import runpy

        runpy.run_path(str(target), run_name="__main__")
        return

    if cmd == "cases":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        from run_test_cases import main as cases_main

        raise SystemExit(cases_main())

    print(f"Unknown command: {cmd}")
    print("Usage: checklist-backend.exe [api|explore|run|cases] [args...]")
    sys.exit(1)


if __name__ == "__main__":
    main()
