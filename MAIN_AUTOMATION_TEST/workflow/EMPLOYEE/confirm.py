# -*- coding: utf-8
"""EMPLOYEE — Xác nhận task (EMP-CFM-*)."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import fail_result, pass_result


def _open_employee_detail(ctx: WorkflowContext) -> bool:
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return False
    return ui.open_first_list_row(ctx)


def emp_cfm_01(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    if not _open_employee_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet de xac nhan")
    if not ui.click_task_confirm_on_time(ctx):
        return ui.fail_with_shot(ctx, "Khong thay nut [Dung han] tren task employee")
    text = ui.autotest_text(ctx)
    ui.fill_modal_text(ctx, text)
    ui.confirm_modal(ctx)
    ui.shot(ctx, "emp_confirm_result")
    return pass_result("EMPLOYEE xac nhan task (BR-01) — khong can officer truoc", note=text)


def emp_cfm_02(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    if not _open_employee_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet")
    late_btn = ctx.page.locator("button:has-text('Muộn')").first
    if not late_btn.count():
        return ui.fail_with_shot(ctx, "Khong co task qua han — can du lieu overdue")
    late_btn.click()
    ctx.page.wait_for_timeout(800)
    ui.shot(ctx, "emp_late_modal")
    text = ui.autotest_text(ctx)
    ui.fill_modal_text(ctx, text)
    ui.confirm_modal(ctx)
    ui.shot(ctx, "emp_confirm_result")
    return pass_result("EMPLOYEE xac nhan muon voi ly do (BR-03)", reason=text)


def emp_cfm_03(ctx: WorkflowContext) -> dict:
    ctx.login_as("EMPLOYEE")
    if not _open_employee_detail(ctx):
        return ui.fail_with_shot(ctx, "Khong co chi tiet")
    if not ui.open_journal_modal(ctx):
        return ui.fail_with_shot(ctx, "Khong mo duoc Nhat ky")
    ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(400)
    if ui.click_quay_lai(ctx):
        return pass_result("Nhat ky + Quay lai danh sach OK")
    return ui.fail_with_shot(ctx, "Quay lai that bai")
