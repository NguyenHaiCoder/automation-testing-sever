# -*- coding: utf-8 -*-
"""Helpers for reading/writing testcase JSON."""
from __future__ import annotations

import json
from datetime import datetime

from api.paths import DATA_DIR, DATA_JSON


def compute_stats(cases: list[dict]) -> dict:
    stats = {"pass": 0, "fail": 0, "untested": 0, "na": 0, "total": len(cases)}
    for case in cases:
        result = str(case.get("result") or "Untested")
        if result == "Pass":
            stats["pass"] += 1
        elif result == "Fail":
            stats["fail"] += 1
        elif result == "N/A":
            stats["na"] += 1
        else:
            stats["untested"] += 1
    return stats


def save_testcases(data: dict) -> dict:
    cases = data.get("cases") or []
    data["stats"] = compute_stats(cases)
    data["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    if "exportedAt" not in data:
        data["exportedAt"] = data["updatedAt"]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def load_testcases_json() -> dict | None:
    if not DATA_JSON.exists():
        return None
    return json.loads(DATA_JSON.read_text(encoding="utf-8"))
