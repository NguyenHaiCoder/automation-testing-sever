# -*- coding: utf-8 -*-
"""Kết quả Pass/Fail chuẩn cho workflow."""
from __future__ import annotations


def pass_result(message: str, **extra) -> dict:
    return {"result": "Pass", "message": message, **extra}


def fail_result(message: str, **extra) -> dict:
    return {"result": "Fail", "message": message, **extra}
