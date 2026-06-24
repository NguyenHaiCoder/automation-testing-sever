# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — build checklist-backend folder (API + Playwright worker)."""
from pathlib import Path

block_cipher = None
# SPECPATH = .../MAIN_AUTOMATION_TEST/pack
root = Path(SPECPATH).parent
workspace = root.parent

datas = [
    (str(root / "accounts.env"), "."),
    (str(root / "data" / "testcases.json"), "data"),
    (str(root / "config"), "config"),
    (str(root / "run_test_cases.py"), "."),
    (str(root / "explore_checklist.py"), "."),
]
e2e = workspace / "run_checklist_e2e.py"
if e2e.exists():
    datas.append((str(e2e), "."))

hiddenimports = [
    "api",
    "api.server",
    "api.paths",
    "api.runtime",
    "api.services.testcase_store",
    "api.services.export_testcases",
    "api.services.log_manager",
    "api.services.case_result_sync",
    "api.services.job_runner",
    "workflow",
    "workflow.common",
    "workflow.runner",
    "workflow.helpers",
    "workflow.helpers.checklist_ui",
    "workflow.helpers.template_ui",
    "workflow.helpers.outcome",
    "workflow.ADMIN.list",
    "workflow.ADMIN.instance",
    "workflow.ADMIN.detail",
    "workflow.ADMIN.template",
    "workflow.OFFICER.list",
    "workflow.OFFICER.confirm",
    "workflow.EMPLOYEE.list",
    "workflow.EMPLOYEE.confirm",
    "workflow.BR.br_tpl_01",
    "run_test_cases",
    "openpyxl",
    "playwright",
    "playwright.sync_api",
    "explore_checklist",
    "config.settings",
    "src.auth",
    "src.page_explorer",
    "src.ui_deep_explorer",
    "src.logger_util",
]

a = Analysis(
    [str(root / "launcher.py")],
    pathex=[str(root), str(workspace)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="checklist-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="checklist-backend",
)
