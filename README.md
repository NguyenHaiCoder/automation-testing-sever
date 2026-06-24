# Checklist Nhân sự — Automation Testing

Monorepo gồm **Python backend** (`MAIN_AUTOMATION_TEST`) và **React dashboard** (`MAIN_AUTOMATION_TEST_FE`).

Repository: https://github.com/NguyenHaiCoder/automation-testing-sever.git

Deploy cloud: xem **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)** (Render, Docker, 1 Web Service).

## Cấu trúc

| Thư mục | Vai trò |
|---------|---------|
| `MAIN_AUTOMATION_TEST/` | Playwright workflows, API Python (`python -m api`) |
| `MAIN_AUTOMATION_TEST_FE/` | React + Ant Design dashboard |
| `scripts/` | Script build / chạy public server |

## Dev local (full quyền — IT)

```powershell
# Terminal 1 — API
cd MAIN_AUTOMATION_TEST
copy accounts.env.example accounts.env   # rồi sửa mật khẩu thật
pip install -r requirements.txt
playwright install chromium
python -m api

# Terminal 2 — FE (sidebar đủ 3 mục)
cd MAIN_AUTOMATION_TEST_FE
npm install
npm run dev
```

Mở http://localhost:5173

## Deploy public (1 server — React + Python chung)

Git **chỉ lưu mã nguồn**. Để chạy automation + dashboard cần **máy chủ có Python** (VPS, Railway, Render, máy nội bộ…). GitHub Pages **không** chạy được Python/Playwright.

Build gộp: Python serve cả API lẫn file tĩnh React (`MAIN_AUTOMATION_TEST_FE/dist`).

```bat
scripts\run-public-server.bat
```

Hoặc thủ công:

```powershell
cd MAIN_AUTOMATION_TEST_FE
npm ci
npm run build:web          # VITE_RESTRICT_ADMIN=true

cd ..\MAIN_AUTOMATION_TEST
$env:RESTRICT_ADMIN="1"
$env:API_HOST="0.0.0.0"
python -m api
```

Mở http://localhost:8765 — **Bảng kiểm thử** dùng được; **Quản lý test case** và **Quản lý log** hiển thị *"Vui lòng liên hệ admin"*, không bấm được (FE + API đều chặn).

### Biến môi trường deploy

| Biến | Ý nghĩa |
|------|---------|
| `RESTRICT_ADMIN=1` | Chặn API log + sửa testcases.json |
| `VITE_RESTRICT_ADMIN=true` | Build FE khóa sidebar (đã có trong `build:web`) |
| `API_HOST=0.0.0.0` | Lắng nghe mọi interface |
| `API_PORT=8765` | Cổng HTTP |
| `FE_DIST` | Đường dẫn tùy chọn tới thư mục `dist` |

## Desktop installer (trưởng phòng — full quyền)

Xem `PACKAGING.md` — Electron + PyInstaller, **không** bật `RESTRICT_ADMIN`.

## Đẩy code lên GitHub

```powershell
cd "F:\5.May-2026\H2Q-SOLUTION-TESTER\Checklist Nhân sự"
git init
git remote add origin https://github.com/NguyenHaiCoder/Automation-testing.git
git add .
git status   # kiểm tra KHÔNG có accounts.env
git commit -m "Initial commit: Checklist automation monorepo"
git branch -M main
git push -u origin main
```

> **Quan trọng:** Không commit `accounts.env` (mật khẩu thật). Chỉ dùng `accounts.env.example`.

Nếu repo GitHub đã có commit cũ:

```powershell
git pull origin main --rebase
# giải quyết conflict nếu có
git push -u origin main
```

## Chạy test case

```powershell
cd MAIN_AUTOMATION_TEST
python run_test_cases.py --cases ADM-LST-01 --visible
```
