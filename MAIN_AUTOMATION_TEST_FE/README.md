# Checklist Automation — Frontend

React dashboard (Vite + TypeScript + Ant Design). **Chi frontend** — API chay tai `MAIN_AUTOMATION_TEST`.

## Cau truc (feature-based)

```
src/
  app/                    # Shell, routing view
  features/
    dashboard/            # Bang kiem thu
    testcases/              # CRUD + types + API
    logs/                   # Quan ly log
    automation/             # Kham pha / Bat dau
  shared/                   # http-client, layout, hooks
```

Moi feature export qua `index.ts` — import qua `@/features/...` hoac `@/shared`.

## Chay dev

1. API: `MAIN_AUTOMATION_TEST\run\run-api.bat`
2. FE: `run\run-dev.bat` hoac `npm run dev`

Hoac full stack: `MAIN_AUTOMATION_TEST\run\run-fullstack.bat`

## Deploy

Khong deploy web. Dong goi **Desktop**:

- Dev: `run\run-desktop.bat`
- Build installer: `run\build-installer.bat`
- Chi tiet: xem `PACKAGING.md` o thu muc goc du an
