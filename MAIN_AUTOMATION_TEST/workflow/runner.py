# -*- coding: utf-8 -*-
"""Dispatch test case ID → workflow implementation."""
from __future__ import annotations

from importlib import import_module
from typing import Callable

from playwright.sync_api import Page

from config.settings import Settings
from workflow.common import WorkflowContext

# case_id → "module.path" hoặc "module.path:function"
_REGISTRY: dict[str, str] = {
    # BR
    "BR-TPL-01": "workflow.BR.br_tpl_01",
    # ADMIN — Danh sách (1 file / case)
    "ADM-LST-01": "workflow.ADMIN.adm_lst_01",
    "ADM-LST-02": "workflow.ADMIN.adm_lst_02",
    "ADM-LST-03": "workflow.ADMIN.adm_lst_03",
    "ADM-LST-04": "workflow.ADMIN.adm_lst_04",
    "ADM-LST-05": "workflow.ADMIN.adm_lst_05",
    "ADM-LST-06": "workflow.ADMIN.adm_lst_06",
    "ADM-LST-07": "workflow.ADMIN.adm_lst_07",
    "ADM-LST-08": "workflow.ADMIN.adm_lst_08",
    # ADMIN — Tạo instance
    "ADM-INS-01": "workflow.ADMIN.adm_ins_01",
    "ADM-INS-02": "workflow.ADMIN.adm_ins_02",
    "ADM-INS-03": "workflow.ADMIN.adm_ins_03",
    # ADMIN — Chi tiết
    "ADM-DTL-01": "workflow.ADMIN.adm_dtl_01",
    "ADM-DTL-02": "workflow.ADMIN.adm_dtl_02",
    "ADM-DTL-03": "workflow.ADMIN.adm_dtl_03",
    "ADM-DTL-04": "workflow.ADMIN.adm_dtl_04",
    "ADM-DTL-05": "workflow.ADMIN.adm_dtl_05",
    # ADMIN — Template
    "ADM-TPL-01": "workflow.ADMIN.adm_tpl_01",
    "ADM-TPL-02": "workflow.ADMIN.adm_tpl_02",
    "ADM-TPL-03": "workflow.ADMIN.adm_tpl_03",
    "ADM-TPL-04": "workflow.ADMIN.adm_tpl_04",
    "ADM-TPL-04B": "workflow.ADMIN.adm_tpl_04b",
    "ADM-TPL-05": "workflow.ADMIN.adm_tpl_05",
    "ADM-TPL-06": "workflow.ADMIN.adm_tpl_06",
    "ADM-TPL-07": "workflow.ADMIN.adm_tpl_07",
    "ADM-TPL-08": "workflow.ADMIN.adm_tpl_08",
    # OFFICER — Danh sách
    "OFF-LST-01": "workflow.OFFICER.off_lst_01",
    "OFF-LST-02": "workflow.OFFICER.off_lst_02",
    "OFF-LST-03": "workflow.OFFICER.off_lst_03",
    "OFF-LST-04": "workflow.OFFICER.off_lst_04",
    # OFFICER — Xác nhận
    "OFF-CFM-01": "workflow.OFFICER.off_cfm_01",
    "OFF-CFM-02": "workflow.OFFICER.off_cfm_02",
    "OFF-CFM-03": "workflow.OFFICER.off_cfm_03",
    "OFF-CFM-04": "workflow.OFFICER.off_cfm_04",
    "OFF-CFM-05": "workflow.OFFICER.off_cfm_05",
    "OFF-CFM-06": "workflow.OFFICER.off_cfm_06",
    # EMPLOYEE — Danh sách
    "EMP-LST-01": "workflow.EMPLOYEE.list:emp_lst_01",
    "EMP-LST-02": "workflow.EMPLOYEE.list:emp_lst_02",
    "EMP-LST-03": "workflow.EMPLOYEE.list:emp_lst_03",
    "EMP-LST-04": "workflow.EMPLOYEE.list:emp_lst_04",
    # EMPLOYEE — Xác nhận
    "EMP-CFM-01": "workflow.EMPLOYEE.confirm:emp_cfm_01",
    "EMP-CFM-02": "workflow.EMPLOYEE.confirm:emp_cfm_02",
    "EMP-CFM-03": "workflow.EMPLOYEE.confirm:emp_cfm_03",
}


def has_workflow(case_id: str) -> bool:
    return case_id in _REGISTRY


def _load_run(case_id: str) -> Callable[[WorkflowContext], dict]:
    spec = _REGISTRY[case_id]
    if ":" in spec:
        mod_path, attr = spec.split(":", 1)
        mod = import_module(mod_path)
        run_fn = getattr(mod, attr, None)
    else:
        mod = import_module(spec)
        run_fn = getattr(mod, "run", None)
    if not callable(run_fn):
        raise RuntimeError(f"Workflow {case_id} thieu handler")
    return run_fn


def run_workflow(case: dict, page: Page, settings: Settings, run_dir) -> dict:
    case_id = case["id"]
    if case_id not in _REGISTRY:
        return {"result": "Untested", "message": f"Chua co workflow cho {case_id}"}

    ctx = WorkflowContext(page=page, settings=settings, case=case, run_dir=run_dir)
    run_fn = _load_run(case_id)
    outcome = run_fn(ctx)
    from workflow.helpers.checklist_ui import ensure_case_evidence

    ensure_case_evidence(ctx)
    outcome.setdefault("caseId", case_id)
    outcome["log"] = ctx.log_lines
    return outcome
