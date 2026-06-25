# -*- coding: utf-8 -*-
"""
OFF-CFM-05 — OFFICER hoàn tác xác nhận trong 60 phút khi employee chưa confirm (BR-02).

Luồng self-contained:
1. OFFICER tạo template + checklist quá hạn (employee chưa confirm)
2. Task 1: bấm [Muộn] → xác nhận (officer confirm)
3. Task 1: bấm [Hoàn tác] → xác nhận undo
4. Pass khi toast thành công và task về trạng thái chờ (có lại [Muộn]/[Đúng hạn], mất [Hoàn tác])
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
            f"OFFICER khong tao duoc template [{template_name}]",
            "officer_template_result",
        )

    if not prep.create_overdue_checklist_instance(
        ctx, template_name, OFFICER_CAN_BO, ASSIGN_EMPLOYEE
    ):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc checklist qua han — template [{template_name}]",
            "officer_create_result",
        )

    prep.remember_lst01_template(ctx, template_name)

    if not off.open_officer_detail_for_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong mo duoc chi tiet [{template_name}]",
            "officer_detail",
        )
    ui.shot(ctx, "officer_detail")

    ok_late, reason, err_late = off.confirm_task_late(
        ctx, task_number=1, shot_name="off_confirm_late_task1"
    )
    if not ok_late:
        if err_late:
            return ui.fail_with_shot(
                ctx,
                f"OFFICER [Muon] task 1 — {err_late}",
                "off_confirm_late_task1_error_toast",
                reason=reason,
                error=err_late,
                templateName=template_name,
            )
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong thay nut [Muon] tren task 1",
            "officer_detail",
            templateName=template_name,
        )

    if not ui.task_has_action(ctx, "Hoàn tác", 1) and not ui.task_has_action(ctx, "Undo", 1):
        return ui.fail_with_shot(
            ctx,
            "Sau [Muon] task 1 khong thay nut [Hoan tac] — can officer confirm trong 60 phut (BR-02)",
            "officer_detail",
            templateName=template_name,
        )

    ok_undo, err_undo = off.undo_task_officer(
        ctx, task_number=1, shot_name="off_undo_task1"
    )
    if not ok_undo:
        if err_undo:
            return ui.fail_with_shot(
                ctx,
                f"OFFICER [Hoan tac] task 1 — {err_undo}",
                "off_undo_task1_error_toast",
                error=err_undo,
                templateName=template_name,
                lateReason=reason,
            )
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong bam duoc nut [Hoan tac] tren task 1",
            "officer_detail",
            templateName=template_name,
        )

    ui.shot(ctx, "undo_result")

    return pass_result(
        f"OFF-CFM-05 OK — task 1 [Muon] → [Hoan tac] [{template_name}] (BR-02)",
        templateName=template_name,
        lateReason=reason,
    )
