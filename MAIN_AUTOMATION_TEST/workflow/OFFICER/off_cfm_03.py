# -*- coding: utf-8 -*-
"""
OFF-CFM-03 — OFFICER xác nhận task muộn — bắt buộc lý do (BR-03).

Luồng self-contained:
1. OFFICER tạo template + checklist (StartDate quá khứ → task quá Deadline)
2. Mở chi tiết → bấm [Muộn] task 1 → nhập [Ghi chú] + [Lý do muộn] automationtestver{N} → Xác nhận
3. Pass chỉ khi toast thành công; Fail nếu toast lỗi / không thấy nút Muộn
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

    if not ui.task_action_visible(ctx, "Muộn"):
        return ui.fail_with_shot(
            ctx,
            "Khong co task qua han (nut Muon) — can du lieu overdue",
            "officer_detail",
            templateName=template_name,
        )

    ok, reason, err = off.confirm_task_late(ctx, task_number=1, shot_name="off_confirm_late")
    if not ok:
        if err:
            return ui.fail_with_shot(
                ctx,
                f"OFFICER xac nhan muon task 1 — {err}",
                "off_confirm_late_error_toast",
                reason=reason,
                error=err,
                templateName=template_name,
            )
        return ui.fail_with_shot(
            ctx,
            "OFFICER khong thay nut [Muon] tren task 1",
            "officer_detail",
            templateName=template_name,
        )

    return pass_result(
        f"OFF-CFM-03 OK — officer [Muon] task 1 [{template_name}] (BR-03)",
        templateName=template_name,
        reason=reason,
    )
