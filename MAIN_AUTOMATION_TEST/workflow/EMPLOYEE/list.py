# -*- coding: utf-8 -*-
"""
EMPLOYEE — Danh sách checklist (EMP-LST-*).

EMP-LST-01:
  1. ADMIN tạo template
  2. OFF đăng nhập → [Tạo checklist] (ngày hôm nay, NV TK Chuyên Viên)
  3. OFF đăng xuất → EMP đăng nhập → tìm đúng checklist OFF vừa tạo (BR-10)

EMP-LST-02: EMP đăng nhập → search keyword từ EMP-LST-01.
EMP-LST-03: Đăng nhập bất kỳ role (EMP/OFF/ADMIN) → danh sách có chữ «trễ» là Pass.
"""
from __future__ import annotations

from workflow.EMPLOYEE import emp_lst_prep as prep
from workflow.OFFICER import off_lst_prep as off_prep
from workflow.OFFICER.off_constants import ASSIGN_EMPLOYEE
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def emp_lst_01(ctx: WorkflowContext) -> dict:
    template_name = off_prep.next_assignees_template_name()

    ctx.login_admin()
    if not prep.admin_create_template(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"ADMIN khong tao duoc template [{template_name}]",
            "admin_template_result",
        )
    ui.switch_role_login(ctx, "OFFICER")

    if not prep.officer_create_checklist_today(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"OFFICER khong tao duoc checklist [{template_name}] cho [{ASSIGN_EMPLOYEE}] (ngay hom nay)",
            "officer_create_checklist_result",
        )

    prep.remember_emp_lst_keyword(ctx, template_name)
    ui.shot(ctx, "officer_create_checklist_result")

    prep.logout_and_login_employee(ctx)

    ui.goto_checklist_list(ctx)
    ui.shot(ctx, "employee_list_page")

    ui.search_keyword(ctx, template_name)
    ui.shot(ctx, "employee_list_search")
    matched = prep.rows_matching_keyword(ctx, template_name)
    if matched == 0:
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE khong thay checklist [{template_name}] do OFF vua tao (BR-10)",
            "employee_list_search",
            templateName=template_name,
        )

    ui.shot(ctx, "case_result")
    return pass_result(
        f"EMP-LST-01 OK — OFF tao checklist [{template_name}] → EMP thay ({matched} dong) — BR-10",
        templateName=template_name,
        rowCount=matched,
    )


def emp_lst_02(ctx: WorkflowContext) -> dict:
    keyword, already_employee = prep.ensure_emp_lst_keyword(ctx)
    if not keyword:
        return ui.fail_with_shot(
            ctx,
            "Khong co du lieu checklist — OFF khong tao duoc checklist cho EMP-LST-02",
            "employee_list_page",
        )

    if not already_employee:
        ctx.login_as("EMPLOYEE")

    ui.goto_checklist_list(ctx)
    ui.shot(ctx, "employee_list_page")
    ui.search_keyword(ctx, keyword)
    ui.shot(ctx, "search_result")

    matched = prep.rows_matching_keyword(ctx, keyword)
    if matched == 0:
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE tim [{keyword}] khong co ket qua trong pham vi instance",
            "search_result",
            keyword=keyword,
        )

    ui.shot(ctx, "case_result")
    return pass_result(
        f"EMP-LST-02 OK — EMPLOYEE tim thay [{keyword}] ({matched} dong)",
        keyword=keyword,
        rowCount=matched,
    )


def emp_lst_03(ctx: WorkflowContext) -> dict:
    roles = ("EMPLOYEE", "OFFICER", "ADMIN")
    for role in roles:
        try:
            ctx.login_as(role)
        except Exception as exc:
            ctx.log(f"Bo qua role [{role}]: {exc}", "WARN")
            continue

        ui.goto_checklist_list(ctx)

        if ui.scroll_to_tre_row(ctx):
            ui.shot(ctx, f"overdue_tre_row_{role.lower()}")
            ui.shot(ctx, "case_result")
            return pass_result(
                f"EMP-LST-03 OK — [{role}] cuon den dong co chu 'tre' tren danh sach",
                role=role,
            )

        ui.shot(ctx, f"overdue_list_{role.lower()}")

    return ui.fail_with_shot(
        ctx,
        "Khong thay chu 'tre' tren danh sach — can instance co task qua han (da thu EMPLOYEE/OFFICER/ADMIN)",
        "overdue_badge",
    )


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
