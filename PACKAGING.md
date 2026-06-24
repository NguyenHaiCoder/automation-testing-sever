# Dong goi Desktop — Checklist Tester

Truong phong chi can **cai 1 lan** roi mo shortcut **Checklist Tester**.

## Cau truc

| Thanh phan | Cong nghe | Output |
|------------|-----------|--------|
| FE | Electron + React | `MAIN_AUTOMATION_TEST_FE/release/*.exe` |
| BE | PyInstaller + Playwright | `MAIN_AUTOMATION_TEST/pack/dist/checklist-backend/` |

Electron tu dong khoi dong `checklist-backend.exe api` khi mo app.

## Build lan dau (IT)

```bat
REM 1. Cai Chromium vao goi backend
MAIN_AUTOMATION_TEST\pack\install-playwright.bat

REM 2. Build backend exe
MAIN_AUTOMATION_TEST\pack\build-backend.bat

REM 3. Build installer Electron (gom ca backend)
MAIN_AUTOMATION_TEST_FE\run\build-installer.bat
```

File cai dat: `MAIN_AUTOMATION_TEST_FE/release/ChecklistTester-Setup-1.0.0.exe`

## Dev / test tren may IT

```bat
MAIN_AUTOMATION_TEST_FE\run\run-desktop.bat
```

Hoac sau khi build backend:

```bat
MAIN_AUTOMATION_TEST\run\run-checklist-tester.bat
```

## Truong phong su dung

1. Cai `ChecklistTester-Setup-*.exe`
2. Mo **Checklist Tester** tren Desktop
3. Bam **Khám phá** hoac **Bắt đầu** — Chromium tu chay

Khong can cai Python, Node, hay cau hinh gi them.

## Luu y

- `accounts.env` va `data/testcases.json` nam canh `checklist-backend.exe`
- Log: `log/` (explore), `log-playwright/` (E2E) — cung thu muc backend
- Cap nhat Excel test case: copy file `.xlsx` vao goi hoac dung Import Excel tren UI
