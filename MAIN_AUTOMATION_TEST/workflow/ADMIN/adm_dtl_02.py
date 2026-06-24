# -*- coding: utf-8 -*-
"""ADM-DTL-02 — ADMIN xem nhật ký thay đổi checklist."""
from __future__ import annotations

from workflow.ADMIN.dtl_helpers import open_dtl_checklist_detail
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    ctx.login_admin()
    if not open_dtl_checklist_detail(ctx):
        return ui.fail_with_shot(
            ctx,
            "Khong mo duoc chi tiet checklist co log — can chay ADM-DTL-01 truoc",
            "detail_opened",
        )

    if not ui.open_journal_modal(ctx):
        return ui.fail_with_shot(ctx, "Khong mo duoc modal Nhat ky", "journal_modal")

    log_lines = ui.journal_log_lines(ctx)
    if not log_lines:
        return ui.fail_with_shot(
            ctx,
            "Nhat ky trong — khong co dong log nao sau khi bam [Nhat ky]",
            "journal_modal",
        )

    if not ui.journal_has_dated_entries(ctx):
        return ui.fail_with_shot(
            ctx,
            "Nhat ky khong co dinh dang ngay gio (dd/mm HH:mm)",
            "journal_modal",
        )

    ctx.page.keyboard.press("Escape")
    ctx.page.wait_for_timeout(400)
    sample = log_lines[0][:80]
    return pass_result(
        f"Nhat ky co {len(log_lines)} dong log voi ngay gio",
        logLineCount=len(log_lines),
        sampleLog=sample,
    )
