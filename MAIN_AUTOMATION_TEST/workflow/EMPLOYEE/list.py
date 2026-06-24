# -*- coding: utf-8
"""EMPLOYEE — Danh sách checklist (EMP-LST-*)."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import fail_result, pass_result


def emp_lst_01(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    result = ui.assert_list_page(ctx, "EMPLOYEE")
    if result["result"] == "Fail":
        return result
    rows = ui.data_row_count(ctx)
    if rows == 0:
        return ui.fail_with_shot(ctx, "EMPLOYEE khong thay checklist cua ban than", "list_page")
    ui.shot(ctx, "case_result")
    return pass_result(f"EMPLOYEE chi thay checklist cua minh ({rows} dong) — BR-10")


def emp_lst_02(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, "test")
    ui.shot(ctx, "case_result")
    return pass_result("EMPLOYEE tim kiem trong pham vi instance cua minh")


def emp_lst_03(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    ui.goto_checklist_list(ctx)
    ui.shot(ctx, "overdue_badge")
    if ui.overdue_badge_visible(ctx):
        return pass_result("Hien thi badge overdue tren danh sach")
    return ui.fail_with_shot(ctx, "Khong thay badge overdue — can instance co task tre", "overdue_badge")


def emp_lst_04(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return ui.fail_with_shot(ctx, "Khong co checklist de mo chi tiet")
    if not ui.open_first_list_row(ctx):
        return ui.fail_with_shot(ctx, "Khong mo duoc chi tiet")
    ui.shot(ctx, "detail_from_list_employee")
    if ui.is_detail_page(ctx):
        return pass_result("Mo chi tiet checklist cua EMPLOYEE")
    return ui.fail_with_shot(ctx, "URL khong phai chi tiet", "detail_from_list_employee")
