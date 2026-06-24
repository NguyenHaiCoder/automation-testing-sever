# -*- coding: utf-8 -*-
"""Remove explore-phase evidenceImages from testcases.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clear_json() -> int:
    path = ROOT / "data" / "testcases.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for case in data.get("cases", []):
        case["evidenceImages"] = []
        case["evidence"] = ""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data.get("cases", []))


def clean_generator() -> None:
    path = ROOT / "scripts" / "generate_testcases_v2.py"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\n\s*evidence_images=\[[^\]]*\],", "", text)
    text = re.sub(r"\n\s*evidence_images=\[\n(?:.*?\n)*?\s*\],", "", text, flags=re.MULTILINE)
    text = text.replace("    evidence_images: list[dict] | None = None,\n", "")
    text = text.replace('        "evidenceImages": evidence_images or [],\n', '        "evidenceImages": [],\n')
    text = re.sub(
        r"\ndef img\(role: str, filename: str, name: str\) -> dict:\n"
        r"    return \{\"runId\": RUN_ID, \"rel\": f\"picture/\{role\}/\{filename\}\", \"name\": name\}\n\n\n",
        "\n\n",
        text,
    )
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    n = clear_json()
    clean_generator()
    print(f"Cleared evidence on {n} cases")
