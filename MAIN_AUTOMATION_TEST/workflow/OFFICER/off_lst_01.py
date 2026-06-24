# -*- coding: utf-8 -*-
"""
OFF-LST-01 — OFFICER thấy checklist được giao (BR-10).

Luồng: ADMIN tạo template automationtestver{N}_autotestasignees (2 đầu việc)
→ tạo checklist (NV: TK Chuyên Viên, CB: TK Trưởng phòng) → logout
→ OFFICER tìm đúng tên template → Pass nếu có kết quả.
"""
from __future__ import annotations

from workflow.OFFICER import off_lst_prep as prep
from workflow.OFFICER.off_constants import ASSIGN_EMPLOYEE, OFFICER_CAN_BO
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    template_name = prep.next_assignees_template_name()

    ctx.login_admin()
    if not prep.create_template_two_tasks(ctx, template_name, OFFICER_CAN_BO):
        return ui.fail_with_shot(
            ctx,
            f"ADMIN khong tao duoc template [{template_name}] (2 dau viec)",
            "admin_template_result",
        )
    if not prep.create_checklist_instance(ctx, template_name, OFFICER_CAN_BO, ASSIGN_EMPLOYEE):
        return ui.fail_with_shot(
            ctx,
            f"ADMIN khong tao duoc checklist — template [{template_name}], NV [{ASSIGN_EMPLOYEE}]",
            "create_result",
        )

    ui.switch_role_login(ctx, "OFFICER")
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, template_name)
    ui.shot(ctx, "officer_search_result")

    if not prep.list_shows_checklist(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tim thay checklist [{template_name}] sau tim kiem",
            "officer_search_result",
        )

    rows = ui.data_row_count(ctx)
    prep.remember_lst01_template(ctx, template_name)
    return pass_result(
        f"OFFICER tim thay checklist [{template_name}] ({rows} dong)",
        templateName=template_name,
        rowCount=rows,
    )
