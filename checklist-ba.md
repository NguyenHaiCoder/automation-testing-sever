# BA Specification — Tính năng Checklist Nhân sự
**Version:** 2.0 — Redesign
**Scope:** FE + BE coordination
**Thay đổi v1 → v2:** xác nhận song song (bỏ thứ tự officer→employee) · officer mặc định định sẵn ở template · thêm % tiến độ · sửa tên/phòng ban/chức vụ hiển thị. Chi tiết §12 Gap-analysis.

---

## 1. Tổng quan

**Mục đích:** Theo dõi và xác nhận hoàn thành các đầu việc bắt buộc theo từng giai đoạn nhân sự (thử việc, onboarding, nghỉ việc…). Cán bộ phụ trách và nhân viên cùng xác nhận từng bước, có minh chứng, nhật ký thay đổi và thông báo kịp thời.

### 1.1 Actor

| Vai trò | Ký hiệu | Mục tiêu chính |
|---------|---------|----------------|
| HR Admin | ADMIN | Tạo/sửa template, tạo & hủy instance, giám sát toàn bộ tiến độ |
| Cán bộ phụ trách | OFFICER | Thực hiện + xác nhận các đầu việc được giao (per-task) |
| Nhân viên | EMPLOYEE | Xác nhận các đầu việc liên quan tới bản thân |
| System | SYSTEM | Auto: tính deadline, đổi trạng thái overdue/completed, gửi thông báo |

### 1.2 Use case chính

| UC | Actor | Mô tả |
|----|-------|-------|
| UC-01 Quản lý template | ADMIN | CRUD template (section + task + officer mặc định/task), bật/tắt |
| UC-02 Tạo checklist | ADMIN | Chọn template + nhân viên (1/nhiều) + StartDate → sinh instance + task_item, officer tự áp từ template |
| UC-03 Xác nhận task (officer) | OFFICER | Confirm đúng hạn/muộn + minh chứng; undo ≤60' |
| UC-04 Xác nhận task (employee) | EMPLOYEE | Confirm đúng hạn/muộn + minh chứng |
| UC-05 Đổi cán bộ task | OFFICER/ADMIN | Đổi người phụ trách 1 task chưa confirm |
| UC-06 Hủy checklist | ADMIN | Hủy instance + lý do (nghỉ việc/chuyển bộ phận) |
| UC-07 Theo dõi tiến độ | ALL | Xem % hoàn thành + trạng thái + nhật ký |

---

## 2. Luồng nghiệp vụ tổng thể

```
[ADMIN] Tạo template (một lần, tái sử dụng)
        → Mỗi task gán Officer mặc định (DefaultOfficerId)
          │
          ▼
[ADMIN] Tạo instance từ template
        → Chọn nhân viên (1 hoặc nhiều) + StartDate
        → System sinh checklist_instance + task_item
        → AssignedOfficerId mỗi task = DefaultOfficerId của template task
        → Notify các OFFICER được giao
          │
          ▼
   Officer & Employee xác nhận ĐỘC LẬP — KHÔNG thứ tự
    ┌──────────────────────────┬──────────────────────────┐
    ▼                          ▼                          ▼
[OFFICER] xác nhận task    [EMPLOYEE] xác nhận task   [OFFICER] đổi cán bộ
 (đúng hạn / muộn + lý do)  (đúng hạn / muộn + lý do)  (task chưa confirm)
 undo ≤60' nếu employee
 chưa confirm task đó
          │
          ▼
   Task done = OfficerStatus ∈ {1,3} AND EmployeeStatus ∈ {1,3}
          │
          ▼
   Tất cả task done → [SYSTEM] Instance → Completed → Notify ADMIN + EMPLOYEE
```

**Trường hợp đặc biệt:** Nhân viên nghỉ việc / chuyển bộ phận → ADMIN hủy instance (lý do, ghi log, notify OFFICER + EMPLOYEE).

---

## 3. Database Schema

> ⚠️ Mọi cột GUID (PK + FK) **dùng `CHAR(36)`**, không `VARCHAR(36)` — DBMA chỉ map DB string → C# `Guid` khi `CHAR(36)`.

### 3.1 `checklist_template`
> Kế thừa `AuditableEntity<Guid>` — Id sinh ở C# bằng `Guid.NewGuid()`.

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | GUID từ C# |
| `Code` | VARCHAR(100) UNIQUE | ✅ | Không dấu, VD `BHS_NhanSuMoi_2025` |
| `Name` | NVARCHAR(255) | ✅ | Tên hiển thị |
| `Description` | NVARCHAR(MAX) | ❌ | Ghi chú nội bộ |
| `IsActive` | BIT DEFAULT 1 | ✅ | Soft disable |
| `IsDeleted` | BIT DEFAULT 0 | ✅ | Soft delete |
| `CreatedBy/At`, `LastUpdatedBy/At` | | | Từ `AuditableEntity` |

### 3.2 `checklist_template_section`

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | |
| `TemplateId` | CHAR(36) FK | ✅ | |
| `Name` | NVARCHAR(255) | ✅ | VD `I. Hành Chính - Văn Phòng` |
| `SortOrder` | INT | ✅ | |
| `IsDeleted` | BIT DEFAULT 0 | ✅ | |

### 3.3 `checklist_template_task`

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | |
| `SectionId` | CHAR(36) FK | ✅ | |
| `Description` | NVARCHAR(MAX) | ✅ | Nội dung đầu việc |
| `DurationDays` | INT | ✅ | Số ngày calendar từ StartDate |
| `DefaultOfficerId` | **CHAR(36) NULL** | ❌ | 🆕 v2 — officer mặc định, instance tự áp. Null → dùng fallback officer lúc tạo |
| `SortOrder` | INT | ✅ | |
| `IsDeleted` | BIT DEFAULT 0 | ✅ | |

### 3.4 `checklist_instance`

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | |
| `TemplateId` | CHAR(36) FK | ✅ | |
| `EmployeeId` | CHAR(36) | ✅ | GUID nhân viên áp dụng |
| `StartDate` | DATE | ✅ | Dùng tính deadline |
| `EndDate` | DATE | ✅ | = MAX(Deadline task), tự tính khi tạo |
| `Status` | TINYINT | ✅ | Xem §4.1 |
| `CancelReason` | NVARCHAR(MAX) | ❌ | Bắt buộc khi Cancelled |
| `CancelledBy/At` | CHAR(36) / DATETIME | ❌ | |
| `IsDeleted` | BIT DEFAULT 0 | ✅ | |
| `CreatedBy/At` | CHAR(36) / DATETIME | ✅ | |

**Constraint:** UNIQUE(`TemplateId`, `EmployeeId`) WHERE `Status NOT IN (2, 4)`.

### 3.5 `checklist_task_item`

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | |
| `InstanceId` | CHAR(36) FK | ✅ | |
| `TemplateTaskId` | CHAR(36) FK | ✅ | |
| `AssignedOfficerId` | CHAR(36) | ✅ | Per-task; khởi tạo = `DefaultOfficerId` |
| `Deadline` | DATE | ✅ | = `StartDate` + `DurationDays` |
| `OfficerStatus` | TINYINT DEFAULT 0 | ✅ | §4.2 |
| `OfficerConfirmedAt/By` | DATETIME / CHAR(36) | ❌ | |
| `OfficerNote` | NVARCHAR(MAX) | ❌ | Minh chứng cán bộ |
| `OfficerLateReason` | NVARCHAR(MAX) | ❌ | Bắt buộc nếu OfficerStatus = Late |
| `EmployeeStatus` | TINYINT DEFAULT 0 | ✅ | §4.2 |
| `EmployeeConfirmedAt/By` | DATETIME / CHAR(36) | ❌ | |
| `EmployeeNote` | NVARCHAR(MAX) | ❌ | Minh chứng nhân viên |
| `EmployeeLateReason` | NVARCHAR(MAX) | ❌ | Bắt buộc nếu EmployeeStatus = Late |
| `IsDeleted` | BIT DEFAULT 0 | ✅ | |

> 🔑 v2: Officer và Employee là **2 cột độc lập**, không ràng buộc thứ tự ghi.

### 3.6 `checklist_log`
> Audit trail — không `IsDeleted`, không bao giờ xóa.

| Column | Type | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| `Id` | CHAR(36) PK | ✅ | |
| `InstanceId` | CHAR(36) FK | ✅ | |
| `TaskItemId` | CHAR(36) FK | ❌ | NULL = log cấp instance |
| `ActorId` | CHAR(36) | ✅ | |
| `Action` | VARCHAR(100) | ✅ | §4.3 |
| `Detail` | NVARCHAR(MAX) | ❌ | |
| `CreatedAt` | DATETIME | ✅ | |

---

## 4. Bảng trạng thái & hằng số

### 4.1 `checklist_instance.Status`

| Giá trị | Tên | Điều kiện chuyển | Ai chuyển |
|---------|-----|-----------------|-----------|
| `0` | Pending | Mới tạo, chưa task nào có confirm | System |
| `1` | InProgress | Có ≥1 task với OfficerStatus≠0 **HOẶC** EmployeeStatus≠0 (bỏ ràng buộc thứ tự) | System (auto) |
| `2` | Completed | Mọi task: Officer ∈ {1,3} AND Employee ∈ {1,3} | System (auto) |
| `3` | Overdue | Có task quá Deadline chưa xử lý | System (job) |
| `4` | Cancelled | ADMIN hủy thủ công | ADMIN |

### 4.2 `OfficerStatus` / `EmployeeStatus`

| Giá trị | Tên | Mô tả |
|---------|-----|-------|
| `0` | Pending | Chưa xử lý |
| `1` | Confirmed | Xác nhận đúng hạn |
| `2` | Undone | Đã undo (officer, ≤60') |
| `3` | Late | Xác nhận quá hạn — bắt buộc LateReason |

**Task done:** OfficerStatus ∈ {1,3} AND EmployeeStatus ∈ {1,3}.

### 4.3 `checklist_log.Action`

`CreateInstance` · `CancelInstance` · `ChangeOfficer` (`OldId→NewId`) · `OfficerConfirm` · `OfficerConfirmLate` · `OfficerUndo` · `EmployeeConfirm` · `EmployeeConfirmLate` · `TaskOverdue` · `InstanceCompleted`.

---

## 5. Phân loại trường (keep / drop / computed / display-only)

### 5.1 Giữ (cốt lõi nghiệp vụ)
Template: `Code, Name, Description, IsActive`, section `Name/SortOrder`, task `Description/DurationDays/SortOrder`.
Instance: `TemplateId, EmployeeId, StartDate, Status, CancelReason`.
Task item: `AssignedOfficerId, OfficerStatus, EmployeeStatus, *Note, *LateReason, *ConfirmedAt/By`.

### 5.2 Thêm mới (v2)
| Trường | Bảng | Lý do |
|--------|------|-------|
| `DefaultOfficerId` | template_task | Khỏi gán tay từng task lúc tạo |

### 5.3 Bỏ / không hiển thị
| Trường | Nơi | Lý do |
|--------|-----|-------|
| `pendingTaskCount` | list response | Suy ra được từ `total - done`; trùng tiến độ |

### 5.4 Tính toán (KHÔNG lưu DB — BE tính, trả qua API)
| Trường | Công thức |
|--------|-----------|
| `deadline` (task) | `StartDate + DurationDays` |
| `endDate` (instance) | `MAX(deadline)` |
| `doneTaskCount` | số task done / instance |
| `totalTaskCount` | tổng task / instance |
| `progressPercent` | `done / total * 100` |
| `overdueTaskCount` | task quá hạn chưa xử lý |
| `canOfficerUndo` | `OfficerConfirmedAt + 60' > NOW AND EmployeeStatus = 0` |
| `officerUndoDeadline` | `OfficerConfirmedAt + 60'` (null nếu hết quyền undo) |
| `isLate` | confirm sau `deadline` |

### 5.5 Display-only (chỉ hiển thị, JOIN bảng dùng chung — KHÔNG sửa schema)
> Mỗi người (employee + officer) hiện **2 trường tên**. Bảng user/phòng ban/chức vụ chỉ JOIN đọc, không ALTER.

| Trường | Nguồn | Quy tắc |
|--------|-------|---------|
| `fullName` | `user.FullName` (JOIN) | Tên đầy đủ — employee + officer |
| `accountName` | `user.AccessControlProfileName ?? user.Username` (JOIN) | Tên tài khoản — employee + officer |
| `position` | bảng chức vụ có sẵn (JOIN) | Chỉ màn **chi tiết** |
| `department` | bảng phòng ban có sẵn (JOIN) | Chỉ màn **chi tiết** |
| `logs[]` | checklist_log | Read-only (actor cũng hiện fullName + accountName) |

---

## 6. API Endpoints

### ChecklistTemplateController — `/api/checklist-template`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| GET | `/getList` | ADMIN | Danh sách template, filter + phân trang |
| GET | `/getDetail` | ADMIN | Chi tiết (sections + tasks + DefaultOfficer) |
| POST | `/insert` | ADMIN | Tạo mới |
| POST | `/update` | ADMIN | Sửa (khi không có instance active) |
| PATCH | `/toggleActive` | ADMIN | Bật/tắt |

### ChecklistAssignmentController — `/api/checklist-assignment`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| GET | `/getCheckList` | ALL | Filter Keyword/FromDate/ToDate/FilterType/EmployeeId/Status + phân trang |
| GET | `/getDetail` | ALL* | Chi tiết (sections + tasks + logs + tiến độ + position/department) |
| POST | `/insertBulk` | ADMIN | Tạo nhiều instance cùng template |
| PATCH | `/cancel` | ADMIN | Hủy (bắt buộc CancelReason) |

*ADMIN xem tất cả; OFFICER + EMPLOYEE chỉ xem instance liên quan mình.

### ChecklistTaskController — `/api/checklist-task`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| PATCH | `/changeOfficer` | OFFICER/ADMIN | Đổi cán bộ 1 task (OfficerStatus ∈ {0,2}) |
| POST | `/officerConfirm` | OFFICER | Xác nhận (đúng hạn/muộn) |
| PATCH | `/officerUndo` | OFFICER | Undo ≤60', employee task đó chưa confirm |
| POST | `/employeeConfirm` | EMPLOYEE | Xác nhận (đúng hạn/muộn) — **không cần officer confirm trước** |

---

## 7. Request / Response (điểm khác v1)

### GET /getCheckList — Response (v2)
```json
{
  "total": 5,
  "items": [
    {
      "instanceId": "...",
      "templateName": "BHS_Checklist hết thời gian thử việc",
      "employeeId": "...",
      "employeeFullName": "Nguyễn Quang Bảo",   // user.FullName (JOIN)
      "employeeAccountName": "BaoNQb",           // AccessControlProfileName ?? Username
      "startDate": "2024-11-19",
      "endDate": "2024-12-20",
      "status": 1,
      "doneTaskCount": 7,                     // 🆕
      "totalTaskCount": 10,                   // 🆕  → progress = 70%
      "overdueTaskCount": 1                   // giữ làm badge; bỏ pendingTaskCount
    }
  ]
}
```

### POST /insertBulk — Request
```json
{
  "templateId": "...",
  "startDate": "2024-11-19",
  "assignedOfficerId": "TrangDT",   // fallback: chỉ dùng cho task có DefaultOfficerId = null
  "employeeIds": ["BaoNQb", "LongLDB"]
}
```
> Quy tắc gán officer khi tạo: `task_item.AssignedOfficerId = template_task.DefaultOfficerId ?? request.assignedOfficerId`. Nếu cả hai null → lỗi validate.

### GET /getDetail — Response (bổ sung v2)
```json
{
  "instanceId": "...",
  "templateName": "...",
  "status": 1,
  "startDate": "2024-11-19",
  "endDate": "2024-12-20",
  "doneTaskCount": 7, "totalTaskCount": 10, "progressPercent": 70,   // 🆕
  "employee": {
    "id": "...",
    "fullName": "Nguyễn Quang Bảo",          // user.FullName (JOIN)
    "accountName": "BaoNQb",                   // ACProfileName ?? Username
    "position": "Chuyên viên",                // JOIN bảng chức vụ có sẵn
    "department": "BAI/Bộ phận AI Gov"         // JOIN bảng phòng ban có sẵn
  },
  "sections": [ { "sectionId": "...", "name": "...", "sortOrder": 1,
    "tasks": [ {
      "taskItemId": "...", "description": "...", "deadline": "2024-12-20", "durationDays": 31,
      "assignedOfficerId": "...", "officerFullName": "Loan HT", "officerAccountName": "LoanHT",  // JOIN user
      "officerStatus": 1, "officerConfirmedAt": "...", "officerNote": "...", "officerLateReason": null,
      "canOfficerUndo": false, "officerUndoDeadline": null,
      "employeeStatus": 0, "employeeConfirmedAt": null, "employeeNote": null, "employeeLateReason": null,
      "logs": [ { "createdAt": "...", "actorId": "...", "actorFullName": "...", "actorAccountName": "...", "action": "ChangeOfficer", "detail": "TrangDT→LoanHT" } ]
    } ] } ]
}
```

---

## 8. Business Rules

| # | Rule | Chi tiết |
|---|------|----------|
| BR-01 | **Xác nhận song song** | OFFICER và EMPLOYEE xác nhận độc lập, **không ràng buộc thứ tự**. Bên nào xong trước cũng được |
| BR-02 | Undo Officer | ≤60' sau OfficerConfirmedAt **VÀ** EmployeeStatus của task đó = 0 (chưa confirm). Sau khi task done → khóa undo |
| BR-03 | Lý do muộn | Bắt buộc với cả OFFICER và EMPLOYEE khi confirm sau Deadline |
| BR-04 | Đổi cán bộ | Chỉ task có OfficerStatus ∈ {0, 2} |
| BR-05 | Auto complete | Instance Status=2 khi mọi task: Officer ∈ {1,3} AND Employee ∈ {1,3} |
| BR-06 | Không duplicate | Không tạo instance mới nếu đã có instance cùng TemplateId + EmployeeId, Status ∈ {0,1,3} |
| BR-07 | Hủy instance | Chỉ ADMIN. Bắt buộc CancelReason. Notify OFFICER + EMPLOYEE |
| BR-08 | Sửa template | Chỉ khi không có instance Status ∈ {0,1,3} |
| BR-09 | Deadline | Theo ngày calendar, không trừ T7/CN |
| BR-10 | Phân quyền | ADMIN xem tất cả; OFFICER xem instance có task mình; EMPLOYEE chỉ xem instance bản thân |
| BR-11 | Soft delete | Mọi bảng (trừ `checklist_log`) dùng `IsDeleted=1`, query thêm `WHERE IsDeleted = 0` |
| BR-12 | **Officer mặc định** | Tạo instance: `AssignedOfficerId = DefaultOfficerId ?? request.assignedOfficerId`. Cả hai null → validate fail |
| BR-13 | **Tên hiển thị** | Mỗi người hiện 2 trường: `fullName` = `user.FullName`; `accountName` = `AccessControlProfileName ?? Username`. BE resolve qua JOIN cho employee + officer + actor log |
| BR-14 | **Không sửa bảng dùng chung** | user / phòng ban / chức vụ chỉ JOIN đọc, KHÔNG ALTER. Chỉ bảng `checklist_*` (của feature) được thêm cột (vd `DefaultOfficerId`) |

---

## 9. Notification

**Kênh:** In-app + Email (SignalR + Redis backplane).

| Sự kiện | Gửi cho | Nội dung |
|---------|---------|----------|
| Tạo instance | OFFICER được giao | "Bạn được giao checklist [Template] cho [Employee]" |
| Đổi cán bộ | OFFICER mới | "Bạn được giao task [TaskDesc] — [Template]/[Employee]" |
| Task done (cả 2 confirm) | — | (không cần notify chéo vì bỏ thứ tự) |
| Task sắp đến hạn (T-2) | Bên chưa confirm | "Task [TaskDesc] đến hạn [Deadline]" |
| Task quá hạn | Bên chưa confirm + ADMIN | "Task [TaskDesc] quá hạn [N] ngày" |
| Instance bị hủy | OFFICER liên quan + EMPLOYEE | "Checklist [Template]/[Employee] đã hủy. Lý do: [CancelReason]" |
| Instance hoàn thành | ADMIN + EMPLOYEE | "Checklist [Template] đã hoàn thành" |

> v2 bỏ notify "đến lượt employee" vì không còn thứ tự — cả 2 nhận task ngay khi tạo instance.

---

## 10. Background Job — ChecklistOverdueJob

- **Chạy:** Hằng ngày 00:05.
- **Tìm:** `task_item` có `Deadline < TODAY` AND (`OfficerStatus = 0` OR `EmployeeStatus = 0`) AND `instance.Status ≠ 4`.
- **Hành động:** set bên nào còn `=0` thành `3` (Late) **độc lập** (không cần bên kia done trước) · ghi log `TaskOverdue` · set `instance.Status = 3` nếu đang 0/1 · gửi notification overdue.

---

## 11. Màn hình FE

> ⚠️ v2 **không thiết kế lại UI** — layout hiện tại tạm ổn, sẽ tinh chỉnh session khác. Mục này chỉ liệt kê màn + dữ liệu BE phải cấp.

| Màn | Route | Role | Dữ liệu v2 cần thêm |
|-----|-------|------|---------------------|
| Danh sách checklist | `/hrm/checklist` | ALL | `employeeName` resolved, `doneTaskCount/totalTaskCount` (thanh %), `overdueTaskCount` badge |
| Chi tiết checklist | `/hrm/checklist/:instanceId` | ALL* | `progressPercent` (vòng tròn/thanh), `position`, `department`, officer name resolved |
| Quản lý template | `/hrm/checklist/template` | ADMIN | field `DefaultOfficerId` mỗi task |

---

## 12. Gap-analysis (v1 → v2)

| Khía cạnh | Hiện trạng (v1) | Thiết kế đề xuất (v2) | Thay đổi cần làm |
|-----------|-----------------|------------------------|------------------|
| Thứ tự xác nhận | Employee chỉ confirm sau officer (BR-01) | Song song, không thứ tự | BE: bỏ check thứ tự ở `employeeConfirm`; sửa BR-01; bỏ notify "đến lượt employee" |
| Officer per-task | Gán 1 người lúc tạo → đổi tay từng task | Template task định sẵn `DefaultOfficerId`, instance tự áp | DB: thêm cột `DefaultOfficerId`. BE: insert template lưu officer, insertBulk áp BR-12. FE: thêm field chọn officer/task trong form template |
| Tên hiển thị | `employeeName` null, FE không có tên | 2 trường: `fullName` + `accountName` (`ACProfileName ?? Username`) | BE: JOIN user resolve cho employee + officer + actor log ở getCheckList + getDetail |
| Phòng ban/chức vụ | `EmployeeInfoVm(..., null, null)` — luôn null | Fill ở chi tiết qua JOIN bảng có sẵn | BE: JOIN bảng phòng ban + chức vụ (KHÔNG sửa schema) cấp `position` + `department` trong getDetail |
| Tiến độ | Chỉ có `pendingTaskCount` + `overdueTaskCount` rời rạc | `doneTaskCount/totalTaskCount` + `progressPercent` | BE: tính & trả 3 field; bỏ `pendingTaskCount`. FE: thanh %/vòng tròn list + detail |
| Undo | Gắn với "trước khi employee confirm" | ≤60' AND employee task chưa confirm | BE: cập nhật điều kiện `canOfficerUndo` + validate undo |
| Trạng thái instance | InProgress = có officer confirm | InProgress = có bất kỳ confirm (officer **hoặc** employee) | BE: sửa logic auto-transition |

### Ưu tiên triển khai
1. **DB migration** `DefaultOfficerId` (CHAR(36) NULL) — nền cho mọi thứ.
2. **BE bỏ thứ tự + resolve tên + tính tiến độ** — sửa được sai nghiệp vụ + thiếu thông tin (đau nhất).
3. **FE** fill tên/phòng ban/chức vụ + thanh % + field officer/task template.

> Ranh giới: thay đổi **contract** (response thêm/bớt field) → theo `.claude/rules/contract-sync.md` — **BE merge trước, FE sau**.
