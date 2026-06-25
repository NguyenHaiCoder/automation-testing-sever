# -*- coding: utf-8 -*-
"""
EMPLOYEE — Xác nhận task (EMP-CFM-*).

EMP-CFM-01: OFF tạo checklist → EMP [Đúng hạn] xác nhận trước officer (BR-01).
EMP-CFM-02: OFF tạo checklist quá hạn → EMP [Muộn] + lý do (BR-03).
EMP-CFM-03: Xem [Nhật ký] checklist EMP-CFM-02 (tự [Muộn] nếu chưa chạy 02) → đóng → [Quay lại].
"""
from __future__ import annotations

from workflow.EMPLOYEE import emp_lst_prep as prep
from workflow.OFFICER.off_constants import ASSIGN_EMPLOYEE
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def _employee_confirm_on_time(
    ctx: WorkflowContext,
    *,
    shot_name: str,
) -> tuple[bool, str, str, int | None]:
    """Bấm [Đúng hạn] trên task employee → ghi chú → Xác nhận."""
    for task_num in (1, 2):
        if not ui.click_task_confirm_on_time(ctx, task_number=task_num):
            continue
        note = ui.autotest_text(ctx)
        ui.fill_modal_text(ctx, note)
        ui.shot(ctx, "emp_confirm_modal")
        ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
        if ok:
            return True, note, "", task_num
        return False, note, outcome, task_num

    if ui.click_task_confirm_on_time(ctx):
        note = ui.autotest_text(ctx)
        ui.fill_modal_text(ctx, note)
        ui.shot(ctx, "emp_confirm_modal")
        ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
        if ok:
            return True, note, "", None
        return False, note, outcome, None

    return False, "", "", None


def _employee_confirm_late(
    ctx: WorkflowContext,
    *,
    shot_name: str,
) -> tuple[bool, str, str, int | None]:
    """Bấm [Muộn] → ghi chú + lý do muộn → Xác nhận."""
    for task_num in (1, 2):
        if not ui.click_task_confirm_late(ctx, task_number=task_num):
            continue
        reason = ui.autotest_text(ctx)
        ui.fill_late_confirm_modal(ctx, reason, reason)
        ui.shot(ctx, "emp_late_modal")
        ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
        if ok:
            return True, reason, "", task_num
        return False, reason, outcome, task_num

    if ui.click_task_confirm_late(ctx):
        reason = ui.autotest_text(ctx)
        ui.fill_late_confirm_modal(ctx, reason, reason)
        ui.shot(ctx, "emp_late_modal")
        ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
        if ok:
            return True, reason, "", None
        return False, reason, outcome, None

    return False, "", "", None


def _close_journal(ctx: WorkflowContext) -> None:
    close_btn = ctx.page.locator(
        ".ant-drawer-close, .ant-modal-close, button[aria-label='Close']"
    ).first
    if close_btn.count():
        try:
            close_btn.click(timeout=5000)
        except Exception:
            ctx.page.keyboard.press("Escape")
    else:
        ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(500)
    ui.shot(ctx, "journal_closed")


def _run_emp_cfm_02_late_confirm(
    ctx: WorkflowContext,
) -> tuple[str, int | None, str] | dict:
    """
    Luồng EMP-CFM-02: OFF checklist quá hạn → EMP [Muộn].
    Thành công: (template_name, task_num, reason) + lưu marker.
    Thất bại: dict fail_result.
    """
    template_name = prep.prep_officer_overdue_checklist(ctx)
    if not template_name:
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc checklist qua han cho [{ASSIGN_EMPLOYEE}]",
            "officer_create_checklist_result",
        )
    ui.shot(ctx, "officer_create_overdue_result")

    prep.logout_and_login_employee(ctx)

    if not prep.open_employee_detail_for_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE khong mo duoc chi tiet [{template_name}]",
            "employee_detail",
            templateName=template_name,
        )
    ui.shot(ctx, "employee_detail")

    if not ui.task_action_visible(ctx, "Muộn"):
        return ui.fail_with_shot(
            ctx,
            "Khong co task qua han (nut Muon) — can checklist overdue",
            "employee_detail",
            templateName=template_name,
        )

    ok, reason, err, task_num = _employee_confirm_late(ctx, shot_name="emp_confirm_late")
    if not ok:
        if err:
            return ui.fail_with_shot(
                ctx,
                f"EMPLOYEE xac nhan [Muon] — {err}",
                "emp_confirm_late_error_toast",
                reason=reason,
                error=err,
                templateName=template_name,
                taskNumber=task_num,
            )
        return ui.fail_with_shot(
            ctx,
            "EMPLOYEE khong thay nut [Muon] tren task qua han (BR-03)",
            "employee_detail",
            templateName=template_name,
        )

    ui.shot(ctx, "emp_confirm_result")
    prep.remember_emp_cfm02_checklist(ctx, template_name, task_num)
    return template_name, task_num, reason


def _open_employee_journal(ctx: WorkflowContext, task_num: int | None) -> bool:
    if ui.open_journal_modal(ctx, task_number=task_num):
        return True
    return ui.open_journal_modal(ctx)


def emp_cfm_01(ctx: WorkflowContext) -> dict:
    template_name = prep.prep_officer_checklist_today(ctx)
    if not template_name:
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc checklist cho [{ASSIGN_EMPLOYEE}] (ngay hom nay)",
            "officer_create_checklist_result",
        )
    ui.shot(ctx, "officer_create_checklist_result")

    prep.logout_and_login_employee(ctx)

    if not prep.open_employee_detail_for_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE khong mo duoc chi tiet checklist [{template_name}]",
            "employee_detail",
            templateName=template_name,
        )
    ui.shot(ctx, "employee_detail")

    ok, note, err, task_num = _employee_confirm_on_time(ctx, shot_name="emp_confirm_on_time")
    if not ok:
        if err:
            return ui.fail_with_shot(
                ctx,
                f"EMPLOYEE xac nhan [Dung han] — {err}",
                "emp_confirm_on_time_error_toast",
                note=note,
                error=err,
                templateName=template_name,
                taskNumber=task_num,
            )
        return ui.fail_with_shot(
            ctx,
            "EMPLOYEE khong thay nut [Dung han] — officer chua confirm, employee confirm truoc (BR-01)",
            "employee_detail",
            templateName=template_name,
        )

    ui.shot(ctx, "emp_confirm_result")
    task_label = f"task {task_num}" if task_num else "task"
    return pass_result(
        f"EMP-CFM-01 OK — EMP [{task_label}] [Dung han] truoc officer [{template_name}] (BR-01)",
        templateName=template_name,
        note=note,
        taskNumber=task_num,
    )


def emp_cfm_02(ctx: WorkflowContext) -> dict:
    out = _run_emp_cfm_02_late_confirm(ctx)
    if isinstance(out, dict):
        return out
    template_name, task_num, reason = out
    task_label = f"task {task_num}" if task_num else "task"
    return pass_result(
        f"EMP-CFM-02 OK — EMP [{task_label}] [Muon] [{template_name}] (BR-03)",
        templateName=template_name,
        reason=reason,
        taskNumber=task_num,
    )


def emp_cfm_03(ctx: WorkflowContext) -> dict:
    template_name, task_num = prep.resolve_emp_cfm02_checklist(ctx)

    if template_name:
        ctx.login_as("EMPLOYEE")
        if not prep.open_employee_detail_for_template(ctx, template_name):
            return ui.fail_with_shot(
                ctx,
                f"EMPLOYEE khong mo duoc chi tiet [{template_name}] tu EMP-CFM-02",
                "employee_detail",
                templateName=template_name,
                taskNumber=task_num,
            )
        ui.shot(ctx, "employee_detail")
    else:
        ctx.log("Chua co marker EMP-CFM-02 — tu chay [Muon] truoc khi xem nhat ky", "INFO")
        out = _run_emp_cfm_02_late_confirm(ctx)
        if isinstance(out, dict):
            return out
        template_name, task_num, _reason = out

    if not _open_employee_journal(ctx, task_num):
        return ui.fail_with_shot(
            ctx,
            f"Khong mo duoc [Nhat ky] task {task_num or ''} — checklist [{template_name}]",
            "employee_detail",
            templateName=template_name,
            taskNumber=task_num,
        )

    log_lines = ui.journal_log_lines(ctx)
    if not log_lines:
        return ui.fail_with_shot(
            ctx,
            "Nhat ky trong — can log sau EMP-CFM-02 [Muon]",
            "journal_modal",
            templateName=template_name,
        )

    if not ui.journal_has_dated_entries(ctx):
        return ui.fail_with_shot(
            ctx,
            "Nhat ky khong co dinh dang ngay gio (dd/mm HH:mm)",
            "journal_modal",
            templateName=template_name,
        )

    _close_journal(ctx)

    if not ui.click_quay_lai(ctx):
        return ui.fail_with_shot(
            ctx,
            "Khong bam duoc [Quay lai] ve danh sach",
            "after_quay_lai",
            templateName=template_name,
        )

    ui.shot(ctx, "case_result")
    task_label = f"task {task_num}" if task_num else "checklist"
    return pass_result(
        f"EMP-CFM-03 OK — [Nhat ky] {task_label} [{template_name}] ({len(log_lines)} dong) + [Quay lai]",
        templateName=template_name,
        taskNumber=task_num,
        logLineCount=len(log_lines),
    )
