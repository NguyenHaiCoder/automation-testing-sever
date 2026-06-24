# -*- coding: utf-8 -*-
"""
OFF-CFM-01 — OFFICER mở chi tiết checklist có task được giao.

Luồng: OFFICER (trưởng phòng) tự tạo template + checklist → mở chi tiết task giao cho mình.
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
    body = ctx.page.locator("body").inner_text()
    has_section = "mục" in body.lower() or "đầu việc" in body.lower() or "dau viec" in body.lower()
    has_confirm = ui.task_action_visible(ctx, "Đúng hạn") or ui.task_action_visible(ctx, "Xác nhận")
    has_change = ui.task_action_visible(ctx, "Đổi CB") or ui.task_action_visible(ctx, "Đổi cán bộ")

    if not (has_confirm or has_change):
        return ui.fail_with_shot(
            ctx,
            "Chi tiet mo duoc nhung khong thay nut Xac nhan / Doi can bo tren task",
            "officer_detail",
            templateName=template_name,
        )

    return pass_result(
        f"OFFICER tu tao + mo chi tiet [{template_name}] — co task giao cho minh",
        templateName=template_name,
        hasSection=has_section,
        hasConfirm=has_confirm,
        hasChangeOfficer=has_change,
    )
