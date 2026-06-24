# -*- coding: utf-8 -*-
"""
ADM-DTL-01 — Tiến độ chi tiết sau NV xác nhận task.

Luồng: tạo template (3 mục) → tạo checklist → logout → EMPLOYEE Đúng hạn hết
→ logout → ADMIN kiểm tra count phải 3/3.
"""
from __future__ import annotations

import re

from playwright.sync_api import Locator

from workflow.ADMIN import create_checklist
from workflow.ADMIN.dtl_constants import DTL_EMPLOYEE, DTL_OFFICER, DTL_SECTION_COUNT
from workflow.ADMIN.tpl_helpers import next_template_name
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers import template_ui as tpl
from workflow.helpers.outcome import pass_result


def _fill_input_verified(
    ctx: WorkflowContext,
    inp: Locator,
    value: str,
    label: str,
) -> bool:
    inp.scroll_into_view_if_needed()
    inp.click(timeout=8000)
    inp.fill("")
    ctx.page.wait_for_timeout(350)
    inp.type(value, delay=40)
    ctx.page.wait_for_timeout(500)
    try:
        actual = inp.input_value().strip()
    except Exception:
        actual = (inp.get_attribute("value") or "").strip()
    if actual != value.strip():
        inp.fill(value)
        ctx.page.wait_for_timeout(500)
        try:
            actual = inp.input_value().strip()
        except Exception:
            actual = (inp.get_attribute("value") or "").strip()
    if actual != value.strip():
        ctx.log(f"{label}: gia tri khong khop — can [{value}], co [{actual}]", "WARN")
        return False
    return True


def _fill_template_section(
    ctx: WorkflowContext,
    modal: Locator,
    index: int,
    section_name: str,
) -> bool:
    section_items = modal.locator(".ant-form-item").filter(has_text="Tên mục")
    if section_items.count() <= index:
        ctx.log(f"Khong du o Ten muc — can index {index + 1}, co {section_items.count()}", "WARN")
        return False

    section_item = section_items.nth(index)
    section_item.scroll_into_view_if_needed()
    ctx.page.wait_for_timeout(400)
    name_inp = section_item.locator("input").first
    if not _fill_input_verified(ctx, name_inp, section_name, f"Ten muc #{index + 1}"):
        return False

    task_inputs = modal.locator('input[placeholder*="đầu việc" i], input[placeholder*="dau viec" i]')
    if task_inputs.count() <= index:
        ctx.log(f"Khong du o mo ta dau viec — index {index}", "WARN")
        return False
    task_inp = task_inputs.nth(index)
    task_inp.scroll_into_view_if_needed()
    task_text = f"{section_name} — task {index + 1}"
    if not _fill_input_verified(ctx, task_inp, task_text, f"Dau viec #{index + 1}"):
        return False
    return True


def _create_template(ctx: WorkflowContext, template_name: str, section_name: str) -> bool:
    tpl.goto_template_list(ctx)
    ui.click_button(ctx, "Tạo template mới")
    modal = ctx.page.locator(".ant-modal").filter(has_text=re.compile(r"Tạo template", re.I))
    modal.wait_for(timeout=10000)

    code = template_name.replace(" ", "_").lower()[:40]
    text_inputs = modal.locator("input[type='text'], input:not([type])")
    if text_inputs.count() >= 2:
        _fill_input_verified(ctx, text_inputs.nth(0), code, "Ma template")
        _fill_input_verified(ctx, text_inputs.nth(1), template_name, "Ten template")
    note = modal.locator("textarea").first
    if note.count():
        _fill_input_verified(ctx, note, template_name, "Mo ta template")

    for i in range(DTL_SECTION_COUNT):
        if i > 0:
            add_section = modal.locator("button:has-text('Thêm mục')").first
            if not add_section.count():
                ctx.log("Khong thay nut Them muc", "WARN")
                return False
            add_section.scroll_into_view_if_needed()
            add_section.click()
            ctx.page.wait_for_timeout(1200)
            section_items = modal.locator(".ant-form-item").filter(has_text="Tên mục")
            try:
                section_items.nth(i).wait_for(state="visible", timeout=8000)
            except Exception:
                ctx.log(f"O Ten muc thu {i + 1} chua hien sau Them muc", "WARN")
                return False

        if not _fill_template_section(ctx, modal, i, section_name):
            return False
        ctx.page.wait_for_timeout(500)

    ui.shot(ctx, "template_create_form")
    submit = modal.locator("button:has-text('Tạo'), button:has-text('Lưu')").first
    if not submit.count():
        return False
    submit.click(timeout=8000)
    ctx.page.wait_for_timeout(3500)
    ui.shot(ctx, "template_create_result")
    body = ctx.page.locator("body").inner_text().lower()
    return "thành công" in body or "thanh cong" in body or "/template" in ctx.page.url


def _create_checklist_instance(ctx: WorkflowContext, template_name: str) -> bool:
    ui.goto_checklist_list(ctx)
    create_checklist.open_modal(ctx)
    if not create_checklist.fill_form(
        ctx,
        officer_name=DTL_OFFICER,
        employee_name=DTL_EMPLOYEE,
        template_name=template_name,
    ):
        return False
    ok, _reason = create_checklist.submit(ctx)
    create_checklist.close_modal(ctx)
    return ok


def _capture_detail_url(ctx: WorkflowContext, keyword: str) -> str | None:
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, keyword)
    if ui.data_row_count(ctx) == 0:
        return None
    href = ui.first_row_detail_href(ctx)
    if href:
        return href
    if ui.open_first_list_row(ctx):
        return ctx.page.url if ui.is_detail_page(ctx) else None
    return None


def _open_detail(ctx: WorkflowContext, keyword: str, detail_url: str | None = None) -> bool:
    ui.goto_checklist_list(ctx)
    if detail_url:
        path = ui.checklist_detail_path(detail_url)
        if ui.goto_checklist_detail(ctx, path):
            ui.shot(ctx, "detail_opened")
            return True
    ui.search_keyword(ctx, keyword)
    if ui.data_row_count(ctx) == 0:
        return False
    if ui.open_first_list_row(ctx):
        ui.shot(ctx, "detail_opened")
        return True
    return False


def _employee_confirm_all_on_time(ctx: WorkflowContext, note: str) -> int:
    confirmed = 0
    for _ in range(30):
        btn = ctx.page.locator("button:has-text('Đúng hạn')").first
        try:
            if not btn.count() or not btn.is_visible():
                break
        except Exception:
            break

        try:
            btn.scroll_into_view_if_needed()
            btn.click(timeout=10000)
        except Exception as exc:
            ctx.log(f"Click Dung han loi: {exc}", "WARN")
            ui.shot(ctx, "emp_confirm_error")
            break

        ctx.page.wait_for_timeout(900)
        modal = ctx.page.locator(".ant-modal:visible").last
        try:
            modal.wait_for(state="visible", timeout=10000)
        except Exception:
            ctx.log("Modal xac nhan khong hien sau click Dung han", "WARN")
            ui.shot(ctx, "emp_confirm_error")
            break

        ui.shot(ctx, f"confirm_modal_{confirmed + 1}")
        ui.fill_modal_text(ctx, note)
        ui.confirm_modal(ctx)
        try:
            modal.wait_for(state="hidden", timeout=12000)
        except Exception:
            ctx.page.wait_for_timeout(1500)
        confirmed += 1
        ctx.page.wait_for_timeout(1500)

    ui.shot(ctx, "emp_confirm_all")
    return confirmed


def _parse_progress_counts(ctx: WorkflowContext, expected_total: int) -> tuple[int, int] | None:
    for sel in (
        ".ant-progress-text",
        ".ant-progress-circle .ant-progress-text",
        "[class*='Progress']",
        "[class*='progress-circle']",
    ):
        for node in ctx.page.locator(sel).all():
            try:
                if not node.is_visible():
                    continue
            except Exception:
                continue
            text = node.inner_text().strip()
            m = re.search(r"(\d+)\s*/\s*(\d+)", text)
            if not m:
                continue
            done, total = int(m.group(1)), int(m.group(2))
            if 0 <= done <= total <= 50:
                return done, total

    body = ctx.page.locator("body").inner_text()
    candidates: list[tuple[int, int]] = []
    for m in re.finditer(r"(\d+)\s*/\s*(\d+)", body):
        done, total = int(m.group(1)), int(m.group(2))
        if done > total or total <= 0 or total > 50:
            continue
        if total <= 12 and done > 12:
            continue
        candidates.append((done, total))

    if not candidates:
        return None
    for pair in candidates:
        if pair[1] == expected_total:
            return pair
    return max(candidates, key=lambda p: (p[1], p[0]))


def _run_impl(ctx: WorkflowContext) -> dict:
    template_name = next_template_name(ctx.case)
    section_name = template_name
    expected_total = DTL_SECTION_COUNT
    detail_url: str | None = None

    ctx.login_admin()
    if not _create_template(ctx, template_name, section_name):
        return ui.fail_with_shot(ctx, f"Khong tao duoc template [{template_name}]", "template_create_form")

    if not _create_checklist_instance(ctx, template_name):
        return ui.fail_with_shot(
            ctx,
            f"Khong tao checklist tu template [{template_name}] — CB [{DTL_OFFICER}], NV [{DTL_EMPLOYEE}]",
            "create_result",
        )

    detail_url = _capture_detail_url(ctx, template_name)
    if detail_url:
        ctx.log(f"Da luu URL chi tiet: {detail_url}", "INFO")
    else:
        ctx.log("Khong lay duoc URL chi tiet — se tim bang keyword", "WARN")

    ui.switch_role_login(ctx, "EMPLOYEE")

    if not _open_detail(ctx, template_name, detail_url):
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE khong mo duoc chi tiet checklist [{template_name}]",
            "detail_from_list_employee",
        )

    confirmed_count = _employee_confirm_all_on_time(ctx, template_name)
    if confirmed_count == 0:
        return ui.fail_with_shot(ctx, "EMPLOYEE khong bam duoc nut [Dung han] nao", "emp_confirm_all")
    if confirmed_count < expected_total:
        return ui.fail_with_shot(
            ctx,
            f"EMPLOYEE moi xac nhan {confirmed_count}/{expected_total} task",
            "emp_confirm_all",
            confirmed=confirmed_count,
            expected=expected_total,
        )

    remaining = ctx.page.locator("button:has-text('Đúng hạn')").count()
    ui.shot(ctx, "emp_after_confirm")
    ui.switch_role_login(ctx, "ADMIN")

    if not _open_detail(ctx, template_name, detail_url):
        return ui.fail_with_shot(ctx, f"ADMIN khong mo lai chi tiet [{template_name}]", "detail_progress")

    ui.shot(ctx, "detail_progress")
    progress = _parse_progress_counts(ctx, expected_total)
    if progress is None:
        return ui.fail_with_shot(ctx, "Khong doc duoc tien do dang done/total tren chi tiet", "detail_progress")

    done, total = progress
    if done == 0:
        return ui.fail_with_shot(
            ctx,
            f"FE chua cap nhat count — NV da xac nhan het {expected_total} task nhung tien do van 0/{total}",
            "detail_progress",
            employeeConfirmed=confirmed_count,
            progressDone=done,
            progressTotal=total,
            expectedTotal=expected_total,
            remainingDungHan=remaining,
        )

    if done == total == expected_total:
        return pass_result(
            f"Tien do dung {done}/{total} — khop template {expected_total} muc",
            employeeConfirmed=confirmed_count,
            progressDone=done,
            progressTotal=total,
        )

    return ui.fail_with_shot(
        ctx,
        f"Tien do sai — can {expected_total}/{expected_total}, hien {done}/{total}",
        "detail_progress",
        employeeConfirmed=confirmed_count,
        progressDone=done,
        progressTotal=total,
        expectedTotal=expected_total,
    )


def run(ctx: WorkflowContext) -> dict:
    try:
        return _run_impl(ctx)
    except Exception as exc:
        ctx.log(f"Loi khong mong doi: {exc}", "ERROR")
        return ui.fail_with_shot(ctx, f"Loi khi chay ADM-DTL-01: {exc}", "error_state")
