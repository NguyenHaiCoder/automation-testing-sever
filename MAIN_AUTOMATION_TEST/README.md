# MAIN_AUTOMATION_TEST

Hệ thống automation test Checklist Nhân sự — quy trình tester thực tế.

## Cấu trúc

```
MAIN_AUTOMATION_TEST/
  accounts.env          # TK test (ADMIN / OFFICER / EMPLOYEE)
  api/                  # HTTP API cho React dashboard
    server.py           # Entry HTTP
    paths.py            # Duong dan tap trung
    services/
      testcase_store.py # data/testcases.json
      export_testcases.py
      log_manager.py
      job_runner.py     # explore / E2E
  data/
    testcases.json      # Nguon du lieu test case (JSON)
  config/settings.py    # Routes BA + load env
  src/
    auth.py             # Login
    page_explorer.py    # Explore tables, buttons, links
    logger_util.py
  explore_checklist.py  # Entry: 3 Chromium song song
  run/
    run-api.bat         # API server :8765
    run-fullstack.bat   # API + FE (2 cua so)
    run-explore.bat           # Mo 3 browser, explore UI
    run-explore-headless.bat  # Chay an
  log/
    run_23-06-2026_10-37-23/
      json/           ← *.json
      picture/
        ADMIN/          ← screenshot ADMIN
        OFFICER/
        EMPLOYEE/
      log/            ← *.log
      docs/           ← *.md
    last_run.txt
  docs/checklist-ba.md
```

## Màn hình theo BA (§11)

| Route | Màn | Role |
|-------|-----|------|
| `/hrm/checklist` | Danh sách checklist | ALL |
| `/hrm/checklist/:instanceId` | Chi tiết | ALL* |
| `/hrm/checklist/template` | Mẫu checklist | ADMIN |

## Deep explore (moi)

Moi man se tu dong:
- Chup baseline + tung buoc click
- **Template (ADMIN):** Tao template moi, 3 nut Chuc nang (xem/sua/xoa dialog)
- **Checklist list:** Tim kiem, date filter, dropdown, refresh, Tao checklist (ADMIN)
- **Officer/Employee:** Cung explore list + filter + row detail
- Anh luu `picture/{ROLE}/{page}_{action}.png`
- Chi tiet trong `json/*_explore.json` → `deep_explores[]`


Double-click: **`run/run-explore.bat`**

Hoặc:

```bat
cd MAIN_AUTOMATION_TEST
python explore_checklist.py --visible
```

## Explore làm gì?

1. Login **3 tài khoản song song** (mỗi role 1 Chromium)
2. Vào từng route checklist theo quyền role
3. Ghi **tables** (header, số dòng, empty)
4. Ghi **buttons** (clickable / not_clickable / destructive_skip)
5. Ghi **links** `/hrm/checklist*`
6. Thử click dòng bảng → màn chi tiết (nếu có data)
7. Screenshot + JSON + summary vào `log/run_*/{json,picture,log,docs}/`

## API Server (React dashboard)

```bat
cd MAIN_AUTOMATION_TEST
python -m api
:: hoac double-click run/run-api.bat
```

| Endpoint | Mo ta |
|----------|-------|
| GET /api/testcases | Doc JSON |
| PUT /api/testcases | Luu JSON |
| GET /api/logs | Danh sach log runs |
| POST /api/explore | Kham pha UI |
| POST /api/run | E2E test |

FE React: `MAIN_AUTOMATION_TEST_FE` (proxy `/api` → `:8765`)

Chay full stack: `run/run-fullstack.bat`

## Bước tiếp theo (chưa làm)

- Map explore → test cases Excel
- Flow confirm Officer / Employee
- Filter, tạo instance, template CRUD
