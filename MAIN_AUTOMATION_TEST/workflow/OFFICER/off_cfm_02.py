# -*- coding: utf-8 -*-
"""
OFF-CFM-02 — OFFICER xác nhận task đúng hạn (BR-01), không cần employee confirm trước.

Luồng đầy đủ (self-contained):
1. OFFICER tạo template mới (2 đầu việc) + assign checklist cho [TK Chuyên Viên]
2. OFFICER bấm [Đúng hạn] task 1 → toast thành công
3. EMPLOYEE (TK Chuyên Viên) bấm [Đúng hạn] task 2 → toast thành công (Pass)

Fail khi EMPLOYEE bấm Xác nhận mà hiện toast lỗi (vd. không có quyền) — chụp error_toast.
"""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.OFFICER import off_lst_prep as prep
from workflow.OFFICER.off_constants import ASSIGN_EMPLOYEE, OFFICER_CAN_BO
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    template_name = prep.next_assignees_template_name()

    off.login_officer(ctx)

    if not prep.create_template_two_tasks(ctx, template_name, OFFICER_CAN_BO):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc template [{template_name}] tren Quan ly template",
            "officer_template_result",
        )

    if not prep.create_checklist_instance(ctx, template_name, OFFICER_CAN_BO, ASSIGN_EMPLOYEE):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc checklist — template [{template_name}], NV [{ASSIGN_EMPLOYEE}]",
            "officer_create_result",
        )

    prep.remember_lst01_template(ctx, template_name)

    if not off.open_officer_detail_for_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong mo duoc chi tiet checklist [{template_name}]",
            "officer_detail",
        )
    ui.shot(ctx, "officer_detail")

    ok, note_officer, err_officer = off.confirm_task_on_time(
        ctx, task_number=1, shot_name="off_confirm_task1"
    )
    if not ok:
        if err_officer:
            return ui.fail_with_shot(
                ctx,
                f"OFFICER task 1 — {err_officer}",
                "off_confirm_task1_error_toast",
                note=note_officer,
                error=err_officer,
            )
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong thay nut [Dung han] tren task 1",
            "officer_detail",
            templateName=template_name,
        )

    ui.switch_role_login(ctx, "EMPLOYEE")
    if not off.open_officer_detail_for_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE khong mo duoc chi tiet checklist [{template_name}]",
            "employee_detail",
            templateName=template_name,
        )
    ui.shot(ctx, "employee_detail")

    ok, note_employee, err_employee = off.confirm_task_on_time(
        ctx, task_number=2, shot_name="emp_confirm_task2"
    )
    if not ok:
        if err_employee:
            return ui.fail_with_shot(
                ctx,
                f"EMPLOYEE task 2 — {err_employee}",
                "emp_confirm_task2_error_toast",
                note=note_employee,
                error=err_employee,
                templateName=template_name,
            )
        return ui.fail_with_shot(
            ctx,
            "EMPLOYEE khong thay nut [Dung han] tren task 2",
            "employee_detail",
            templateName=template_name,
        )

    return pass_result(
        f"OFF-CFM-02 OK — officer task 1 + employee task 2 [{template_name}] (BR-01)",
        templateName=template_name,
        officerNote=note_officer,
        employeeNote=note_employee,
    )
