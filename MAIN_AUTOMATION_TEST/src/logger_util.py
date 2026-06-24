# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROLES = ("ADMIN", "OFFICER", "EMPLOYEE")


@dataclass
class RunLayout:
    """Cấu trúc thư mục mỗi lần chạy automation."""

    run_dir: Path

    @property
    def json_dir(self) -> Path:
        return self.run_dir / "json"

    @property
    def picture_dir(self) -> Path:
        return self.run_dir / "picture"

    @property
    def log_dir(self) -> Path:
        return self.run_dir / "log"

    @property
    def docs_dir(self) -> Path:
        return self.run_dir / "docs"

    def picture_dir_for_role(self, role: str) -> Path:
        """picture/ADMIN | OFFICER | EMPLOYEE"""
        d = self.picture_dir / role.upper()
        d.mkdir(parents=True, exist_ok=True)
        return d

    def ensure(self) -> "RunLayout":
        for d in (self.json_dir, self.picture_dir, self.log_dir, self.docs_dir):
            d.mkdir(parents=True, exist_ok=True)
        for role in ROLES:
            (self.picture_dir / role).mkdir(parents=True, exist_ok=True)
        return self


def make_run_folder_name(when: datetime | None = None) -> str:
    """Tên folder: run_23-06-2026_10-37-23"""
    dt = when or datetime.now()
    return dt.strftime("%d-%m-%Y_%H-%M-%S")


def reorganize_run_folder(run_dir: Path) -> dict[str, int]:
    """
    Sắp xếp file lộn xộn ở root run_* vào đúng subfolder.
    Trả về số file đã di chuyển theo loại.
    """
    if not run_dir.is_dir() or not run_dir.name.startswith("run_"):
        return {}

    layout = RunLayout(run_dir).ensure()
    moved = {"json": 0, "picture": 0, "log": 0, "docs": 0}

    mapping = {
        ".json": layout.json_dir,
        ".png": layout.picture_dir,
        ".jpg": layout.picture_dir,
        ".jpeg": layout.picture_dir,
        ".webp": layout.picture_dir,
        ".log": layout.log_dir,
        ".md": layout.docs_dir,
    }

    for item in list(run_dir.iterdir()):
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        target_dir = mapping.get(ext)
        if not target_dir:
            continue
        dest = target_dir / item.name
        if dest.resolve() == item.resolve():
            continue
        if dest.exists():
            dest.unlink()
        shutil.move(str(item), str(dest))
        if ext == ".json":
            moved["json"] += 1
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            moved["picture"] += 1
        elif ext == ".log":
            moved["log"] += 1
        elif ext == ".md":
            moved["docs"] += 1

    pic_moved = reorganize_pictures_by_role(layout.picture_dir)
    if any(pic_moved.values()):
        moved["picture_roles"] = pic_moved

    return moved


def reorganize_pictures_by_role(picture_dir: Path) -> dict[str, int]:
    """Chia anh trong picture/ thanh picture/ADMIN, OFFICER, EMPLOYEE."""
    if not picture_dir.is_dir():
        return {}
    moved = {r: 0 for r in ROLES}
    for role in ROLES:
        (picture_dir / role).mkdir(parents=True, exist_ok=True)

    for png in list(picture_dir.glob("*.png")):
        upper = png.name.upper()
        for role in ROLES:
            prefix = f"{role}_"
            if upper.startswith(prefix):
                new_name = png.name[len(prefix):]
                dest = picture_dir / role / new_name
                if dest.exists():
                    dest.unlink()
                shutil.move(str(png), str(dest))
                moved[role] += 1
                break
    return moved


def reorganize_all_runs(log_base: Path) -> None:
    for run_dir in sorted(log_base.glob("run_*")):
        if run_dir.is_dir():
            reorganize_run_folder(run_dir)


class RunLogger:
    def __init__(self, layout: RunLayout, name: str = "explore"):
        self.layout = layout.ensure()
        self.text_path = self.layout.log_dir / f"{name}.log"
        self._fh = open(self.text_path, "w", encoding="utf-8")
        self._lock = threading.Lock()
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    @property
    def run_dir(self) -> Path:
        return self.layout.run_dir

    def log(self, msg: str, level: str = "INFO"):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}"
        with self._lock:
            self._fh.write(line + "\n")
            self._fh.flush()
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))

    def section(self, title: str):
        self.log("=" * 70)
        self.log(title)
        self.log("=" * 70)

    def save_json(self, name: str, data: dict):
        path = self.layout.json_dir / name
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(f"JSON → json/{path.name}")

    def save_doc(self, name: str, content: str):
        path = self.layout.docs_dir / name
        path.write_text(content, encoding="utf-8")
        self.log(f"DOC → docs/{path.name}")

    def picture_path(self, filename: str) -> Path:
        return self.layout.picture_dir / filename

    def close(self):
        self._fh.close()


def new_run_dir(log_base: Path) -> tuple[Path, str, RunLayout]:
    run_id = make_run_folder_name()
    run_dir = log_base / f"run_{run_id}"
    layout = RunLayout(run_dir).ensure()
    (log_base / "last_run.txt").write_text(str(run_dir), encoding="utf-8")
    return run_dir, run_id, layout
