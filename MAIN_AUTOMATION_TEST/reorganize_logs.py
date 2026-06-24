# -*- coding: utf-8 -*-
"""Sắp xếp lại file log cũ vào json/ picture/ log/ docs/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config.settings import LOG_DIR  # noqa: E402
from src.logger_util import reorganize_all_runs, reorganize_run_folder, reorganize_pictures_by_role  # noqa: E402


def main():
    print(f"Reorganize: {LOG_DIR}")
    for run_dir in sorted(LOG_DIR.glob("run_*")):
        if not run_dir.is_dir():
            continue
        moved = reorganize_run_folder(run_dir)
        pic = reorganize_pictures_by_role(run_dir / "picture")
        if any(moved.values()) or any(pic.values()):
            print(f"  {run_dir.name}: files={moved} pictures_by_role={pic}")
        else:
            print(f"  {run_dir.name}: already organized")
    print("Done.")


if __name__ == "__main__":
    main()
