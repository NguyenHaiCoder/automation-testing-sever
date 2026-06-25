# -*- coding: utf-8 -*-
"""
OFF-CFM-04 — OFFICER đổi cán bộ phụ trách task chưa confirm (BR-04).

Luồng self-contained:
1. OFFICER tạo template + checklist quá hạn (2 task)
2. Task 1: bấm [Muộn] → xác nhận (chuẩn bị trạng thái như màn hình thực tế)
3. Task 2: bấm [Đổi CB] → chọn ngẫu nhiên 1 cán bộ trang 1 → [Lưu]
4. Pass khi toast thành công (AssignedOfficerId đổi — BR-04)
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
            "OFFICER khong thay nut [Muon] tren task 1 (can truoc khi Doi CB task 2)",
            "officer_detail",
            templateName=template_name,
        )

    if not ui.task_action_visible(ctx, "Đổi CB") and not ui.task_action_visible(ctx, "Đổi cán bộ"):
        return ui.fail_with_shot(
            ctx,
            "Task 2 khong co nut [Doi CB] sau khi officer xac nhan muon task 1",
            "officer_detail",
            templateName=template_name,
        )

    ok, new_officer, err = off.change_task_officer(
        ctx,
        task_number=2,
        shot_name="change_officer_task2",
        exclude_officer=OFFICER_CAN_BO,
    )
    if not ok:
        if err:
            return ui.fail_with_shot(
                ctx,
                f"OFFICER [Doi CB] task 2 — {err}",
                "change_officer_task2_error_toast",
                newOfficer=new_officer,
                error=err,
                templateName=template_name,
            )
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong thay nut [Doi CB] tren task 2",
            "officer_detail",
            templateName=template_name,
        )

    return pass_result(
        f"OFF-CFM-04 OK — task 1 [Muon] + task 2 [Doi CB] → [{new_officer}] [{template_name}] (BR-04)",
        templateName=template_name,
        lateReason=reason,
        newOfficer=new_officer,
    )
