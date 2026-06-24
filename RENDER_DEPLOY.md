# Deploy lên Render — Hướng dẫn chi tiết

Repo: https://github.com/NguyenHaiCoder/automation-testing-sever.git

**1 repo, 1 Web Service (Docker)** — Python API + React dashboard cùng URL.

---

## Tổng quan

| Thành phần | Cách deploy |
|------------|-------------|
| React FE | Build trong Docker → `MAIN_AUTOMATION_TEST_FE/dist/` |
| Python API | `python -m api` serve `/api/*` + file tĩnh |
| Playwright | Image `mcr.microsoft.com/playwright/python` (có Chromium) |
| Public mode | `RESTRICT_ADMIN=1` — khóa Quản lý test case & Quản lý log |

URL sau deploy: `https://checklist-automation.onrender.com` (tên có thể khác).

---

## Bước 1 — Chuẩn bị GitHub

Code đã nằm trên `automation-testing-sever`. Mỗi lần push `main` → Render tự build lại (nếu đã connect).

**Không** commit `accounts.env` (mật khẩu). Trên Render dùng **Environment Variables**.

---

## Bước 2 — Tạo tài khoản Render

1. Vào https://render.com → đăng ký / đăng nhập
2. **Account Settings → Connect GitHub**
3. Authorize repo `NguyenHaiCoder/automation-testing-sever`

---

## Bước 3 — Deploy bằng Blueprint (khuyên dùng)

1. Dashboard Render → **New +** → **Blueprint**
2. Connect repository: `automation-testing-sever`
3. Render đọc file `render.yaml` ở root repo
4. Màn hình review → bấm **Apply**

Blueprint tạo Web Service `checklist-automation` với Docker.

---

## Bước 4 — Cấu hình Environment Variables (bắt buộc)

Vào service **checklist-automation** → **Environment** → thêm:

| Key | Ví dụ | Ghi chú |
|-----|-------|---------|
| `BASE_URL` | `https://qlrv.democloud.xyz` | URL app cần test |
| `ADMIN_EMAIL` | `admin@...` | Tài khoản ADMIN |
| `ADMIN_PASSWORD` | `***` | Secret |
| `OFFICER_EMAIL` | `officer@...` | |
| `OFFICER_PASSWORD` | `***` | Secret |
| `EMPLOYEE_EMAIL` | `employee@...` | |
| `EMPLOYEE_PASSWORD` | `***` | Secret |

Các biến sau **đã có** trong `render.yaml` (không cần sửa):

- `RESTRICT_ADMIN=1`
- `HEADLESS=1`
- `API_HOST=0.0.0.0`
- `PARALLEL_BROWSERS=1`

Render tự inject `PORT` — server đọc biến này.

Sau khi thêm env → **Save, rebuild, and deploy**.

---

## Bước 5 — Chờ build xong

1. Tab **Logs** → xem build Docker (5–15 phút lần đầu)
2. Thấy `[API] Listening on http://0.0.0.0:...` → deploy OK
3. Mở URL service → dashboard **Bảng kiểm thử**

### Kiểm tra nhanh

- `https://<your-app>.onrender.com/api/health`  
  → `{"ok":true,"restrictAdmin":true,"feDist":...}`
- Sidebar: 2 mục admin hiện **"Vui lòng liên hệ admin"**, không bấm được

---

## Bước 6 — Deploy thủ công (không dùng Blueprint)

**New + → Web Service**

| Mục | Giá trị |
|-----|---------|
| Repository | `automation-testing-sever` |
| Branch | `main` |
| Runtime | **Docker** |
| Dockerfile path | `./Dockerfile` |
| Docker context | `.` |
| Plan | Free (xem lưu ý bên dưới) |
| Region | Singapore (gần VN) |
| Health Check Path | `/api/health` |

Thêm Environment Variables như Bước 4 → **Create Web Service**.

---

## Plan Free vs Starter

| | Free | Starter (~$7/tháng) |
|---|------|---------------------|
| Xem dashboard / test case | OK | OK |
| Sleep sau 15 phút không dùng | Có (cold start ~30s) | Không sleep |
| RAM | 512 MB | 512 MB+ |
| Chạy Playwright (Khám phá / Bắt đầu) | Dễ OOM / fail | Ổn định hơn |

**Khuyến nghị:** Free để demo dashboard; **Starter** nếu cần chạy automation trên cloud.

Đổi plan: Service → **Settings → Instance Type**.

---

## Cập nhật code sau này

```powershell
git add .
git commit -m "your message"
git push origin main
```

Render tự deploy lại khi push `main`.

---

## Xử lý lỗi thường gặp

### Build fail — npm / pip

- Xem tab **Logs** → dòng lỗi đỏ
- Đảm bảo `package-lock.json` đã commit
- Build local test: `docker build -t checklist-test .`

### 502 / Application failed to respond

- Chưa set `ADMIN_EMAIL` / `BASE_URL` → job Playwright fail nhưng API vẫn phải chạy
- Kiểm tra **Logs** runtime: có `[API] Listening` không
- Health check: `/api/health`

### Trang trắng

- Build FE lỗi → kiểm tra log bước `npm run build:web`
- Mở DevTools → Network: file `assets/*.js` phải 200

### Playwright fail trên Render

- Bật `HEADLESS=1` (đã set)
- Giảm `PARALLEL_BROWSERS=1`
- Nâng plan Starter
- Free tier **không** phù hợp chạy Chromium lâu dài

### Cold start (Free)

Lần đầu mở sau khi sleep → đợi 30–60 giây.

---

## Kiến trúc sau deploy

```
Browser
   │
   ▼
https://xxx.onrender.com
   │
   ├── /              → React (dist/)
   ├── /api/testcases → JSON dashboard
   ├── /api/health    → health check
   └── POST /api/run-cases → Playwright (cần RAM đủ)
```

---

## Local test Docker (trước khi push)

```powershell
cd "F:\...\Checklist Nhân sự"
docker build -t checklist-automation .
docker run --rm -p 8765:10000 -e PORT=10000 -e RESTRICT_ADMIN=1 `
  -e BASE_URL=https://qlrv.democloud.xyz `
  -e ADMIN_EMAIL=... -e ADMIN_PASSWORD=... `
  checklist-automation
```

Mở http://localhost:8765 (map port 10000 container).

---

## Liên hệ / quyền admin

Trên Render public: user chỉ xem **Bảng kiểm thử**.  
Muốn mở Quản lý test case / log → chạy local hoặc Electron desktop (`PACKAGING.md`) với `RESTRICT_ADMIN` tắt.
