# -*- coding: utf-8 -*-
"""
OFF-LST-02 — OFFICER tìm kiếm checklist theo keyword OFF-LST-01.

Phụ thuộc OFF-LST-01: tìm record automationtestver{N}_autotestasignees trong phạm vi quyền.
"""
from __future__ import annotations

from workflow.OFFICER import off_helpers as off
from workflow.OFFICER import off_lst_prep as prep
from workflow.common import WorkflowContext
from workflow.helpers import checklist_ui as ui
from workflow.helpers.outcome import pass_result


def run(ctx: WorkflowContext) -> dict:
    keyword = prep.resolve_lst01_search_keyword(ctx)

    off.login_officer(ctx)
    ui.goto_checklist_list(ctx)
    ui.search_keyword(ctx, keyword)
    ui.shot(ctx, "search_result_officer")

    template_name = prep.resolve_lst01_template(ctx) or keyword
    if not prep.list_shows_checklist(ctx, template_name):
        rows = ui.data_row_count(ctx)
        if rows == 0:
            return ui.fail_with_shot(
                ctx,
                f"Khong co record lien quan OFF-LST-01 sau tim [{keyword}] — chay OFF-LST-01 truoc",
                "search_result_officer",
            )
        return ui.fail_with_shot(
            ctx,
            f"Tim [{keyword}] co {rows} dong nhung khong khop checklist OFF-LST-01",
            "search_result_officer",
            keyword=keyword,
        )

    rows = ui.data_row_count(ctx)
    return pass_result(
        f"OFFICER tim thay record OFF-LST-01 [{template_name}] ({rows} dong)",
        keyword=keyword,
        rowCount=rows,
    )
