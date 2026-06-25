# -*- coding: utf-8 -*-
"""Helper dùng chung OFF-LST / OFF-CFM."""
from __future__ import annotations

from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui


def login_officer(ctx: WorkflowContext) -> None:
    ctx.login_as("OFFICER")


def open_officer_detail_for_template(ctx: WorkflowContext, template_name: str) -> bool:
    """Danh sách checklist → tìm tên → mở chi tiết instance OFF-LST-01."""
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, template_name)
    target = template_name.strip().lower()
    for row in ui.data_table_rows(ctx):
        if target not in row.inner_text().lower():
            continue
        row.click(timeout=8000)
        ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_officer")
            return True
        link = row.locator("a").first
        if link.count():
            link.click(timeout=8000)
            ctx.page.wait_for_timeout(2000)
        if ui.is_detail_page(ctx):
            ui.shot(ctx, "detail_from_list_officer")
            return True
    return False


def open_officer_detail(ctx: WorkflowContext) -> bool:
    ui.goto_checklist_list(ctx)
    if ui.data_row_count(ctx) == 0:
        return False
    if ui.open_first_list_row(ctx):
        ui.shot(ctx, "detail_from_list_officer")
        return True
    return False


def confirm_note(ctx: WorkflowContext) -> str:
    return ui.autotest_text(ctx)


def confirm_task_on_time(
    ctx: WorkflowContext,
    *,
    task_number: int,
    shot_name: str,
) -> tuple[bool, str, str]:
    """
    Bấm [Đúng hạn] → nhập ghi chú → Xác nhận modal.
    Trả về (ok, note, error_message). Fail nếu toast lỗi hoặc modal không đóng.
    """
    if not ui.click_task_confirm_on_time(ctx, task_number=task_number):
        return False, "", ""

    note = confirm_note(ctx)
    ui.fill_modal_text(ctx, note)
    ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
    if not ok:
        return False, note, outcome
    return True, note, ""


def confirm_task_late(
    ctx: WorkflowContext,
    *,
    task_number: int,
    shot_name: str,
) -> tuple[bool, str, str]:
    """Bấm [Muộn] trên task → nhập lý do → Xác nhận modal."""
    if not ui.click_task_confirm_late(ctx, task_number=task_number):
        return False, "", ""

    reason = confirm_note(ctx)
    ui.fill_late_confirm_modal(ctx, reason, reason)
    ui.shot(ctx, "late_confirm_modal")
    ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
    if not ok:
        return False, reason, outcome
    return True, reason, ""


def change_task_officer(
    ctx: WorkflowContext,
    *,
    task_number: int,
    shot_name: str,
    exclude_officer: str | None = None,
) -> tuple[bool, str, str]:
    """
    Bấm [Đổi CB] trên task → chọn cán bộ ngẫu nhiên (trang 1 dropdown) → [Lưu].
    Trả về (ok, officer_name, error_message).
    """
    if not ui.click_task_change_officer(ctx, task_number=task_number):
        return False, "", ""

    modal = ctx.page.locator(".ant-modal:visible").last
    try:
        modal.wait_for(state="visible", timeout=10000)
    except Exception:
        return False, "", "Modal Doi can bo khong hien"

    ui.shot(ctx, "change_officer_modal")
    sel = modal.locator(".ant-select").first
    if not sel.count():
        return False, "", "Khong thay select can bo trong modal"

    sel.click(timeout=8000)
    ctx.page.wait_for_timeout(400)
    exclude = {exclude_officer} if exclude_officer else set()
    chosen = ui.pick_random_select_option(ctx, exclude=exclude)
    if not chosen:
        ui.shot(ctx, "change_officer_no_option")
        return False, "", "Khong chon duoc can bo moi trong dropdown"

    ui.shot(ctx, "change_officer_selected")
    ok, outcome = ui.submit_save_modal(ctx, shot_name)
    if not ok:
        return False, chosen, outcome
    return True, chosen, ""


def undo_task_officer(
    ctx: WorkflowContext,
    *,
    task_number: int,
    shot_name: str,
) -> tuple[bool, str]:
    """
    Bấm [Hoàn tác] trên task đã officer confirm → xác nhận popconfirm → poll toast.
    Trả về (ok, error_message).
    """
    if not ui.click_task_undo(ctx, task_number=task_number):
        return False, ""

    ui.shot(ctx, "undo_confirm_prompt")
    if not ui.confirm_undo_prompt(ctx):
        ctx.page.wait_for_timeout(400)
        if ui.modal_is_visible(ctx):
            ok, outcome = ui.submit_confirm_modal(ctx, shot_name)
            return ok, outcome

    ok, outcome = ui.submit_undo_action(ctx, shot_name)
    if not ok:
        return False, outcome

    has_undo = ui.task_has_action(ctx, "Hoàn tác", task_number) or ui.task_has_action(
        ctx, "Undo", task_number
    )
    has_confirm = (
        ui.task_has_action(ctx, "Đúng hạn", task_number)
        or ui.task_has_action(ctx, "Muộn", task_number)
        or ui.task_has_action(ctx, "Xác nhận", task_number)
    )
    if has_confirm and not has_undo:
        return True, outcome
    if not has_undo:
        return True, outcome
    return False, "Hoan tac khong thay doi trang thai task"
