# -*- coding: utf-8 -*-
"""
Generate testcases.json v2 from explore run + checklist-ba.md.
Run: python scripts/generate_testcases_v2.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.testcase_store import save_testcases  # noqa: E402
from scripts.pass_fail_conditions import apply_conditions  # noqa: E402

RUN_ID = "run_23-06-2026_12-53-02"
EXPLORE_REF = f"Explore: {RUN_ID}"

# automationtestver11, ver12, … — template từ AUTOMATION_TEMPLATE_VERSION_MIN (tpl_constants.py)
TEXT_INPUT_RULE = (
    "Text field: automationtestver{N} (template bắt đầu từ ver11 trở đi, mỗi lần chạy +1). "
    "Trường số: nhập số hợp lệ bình thường."
)



def case(
    id_: str,
    section: str,
    description: str,
    procedure: str,
    expected: str,
    dependence: str = "",
    test_data: str = "",
    result: str = "Untested",
    note: str = "",
) -> dict:
    return {
        "id": id_,
        "section": section,
        "description": description,
        "procedure": procedure,
        "expected": expected,
        "dependence": dependence,
        "testData": test_data,
        "result": result,
        "testDate": "",
        "note": note or EXPLORE_REF,
        "evidence": "",
        "evidenceImages": [],
    }


def build_cases() -> list[dict]:
    c: list[dict] = []

    # ── ADMIN — Danh sách checklist ─────────────────────────────────────
    c.append(case(
        "ADM-LST-01",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN truy cập màn danh sách checklist và thấy toàn bộ instance",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Chọn menu [Checklist nhân sự]\n"
        "3. Chọn submenu [Checklist]\n"
        "4. Truy cập màn hình [Danh sách checklist]",
        "1. Màn [Danh sách checklist] hiển thị đầy đủ\n"
        "2. ADMIN thấy toàn bộ instance trong hệ thống (BR-10)\n"
        "3. Có cột: STT, Nhân viên, Checklist, Từ ngày, Đến ngày, Trạng thái, Tiến độ\n"
        "4. Có button [Tạo checklist]",
        "Tài khoản ADMIN hợp lệ",
        "",
    ))
    c.append(case(
        "ADM-LST-02",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN tìm kiếm checklist theo Keyword",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhập [Keyword] vào ô tìm kiếm: test\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Danh sách chỉ hiển thị record khớp Keyword\n"
        "2. API GET /api/checklist-assignment/getCheckList trả kết quả đã filter",
        "[ADM-LST-01]",
    ))
    c.append(case(
        "ADM-LST-03",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN lọc checklist theo khoảng ngày",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhấn ô chọn khoảng ngày để mở lịch\n"
        "4. Chọn ngày bắt đầu trên lịch\n"
        "5. Chọn ngày kết thúc trên lịch\n"
        "6. Nhấn button [Tìm kiếm]",
        "1. Lịch hiển thị khoảng ngày đã chọn\n"
        "2. Danh sách chỉ hiển thị instance trong khoảng FromDate–ToDate",
        "[ADM-LST-01]",
    ))
    c.append(case(
        "ADM-LST-04",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN lọc checklist — Thực hiện cho NV + nhân viên Quyền Phạm Năng",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Mở dropdown [Trạng thái / phạm vi] → chọn [Thực hiện cho NV]\n"
        "4. Chọn nhân viên [Quyền Phạm Năng] trong dropdown nhân viên\n"
        "5. Quan sát danh sách sau khi lọc",
        "1. Dropdown mở và chọn được [Thực hiện cho NV] + [Quyền Phạm Năng]\n"
        "2. Danh sách chỉ hiển thị nhân viên Quyền Phạm Năng (không có nhân viên khác)",
        "[ADM-LST-01]",
        "Thực hiện cho NV · Quyền Phạm Năng",
    ))
    c.append(case(
        "ADM-LST-05",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN làm mới danh sách checklist",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhấn button [Làm mới]",
        "1. Danh sách được tải lại từ API\n"
        "2. Dữ liệu hiển thị đồng bộ với server",
        "[ADM-LST-01]",
    ))
    c.append(case(
        "ADM-LST-06",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "Hiển thị tiến độ doneTaskCount/totalTaskCount trên danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Quan sát cột [Tiến độ] tại dòng có instance đang InProgress",
        "1. Cột Tiến độ hiển thị dạng done/total (vd: 0/3, 7/10)\n"
        "2. Không hiển thị pendingTaskCount (đã bỏ v2)\n"
        "3. progressPercent có thể suy ra từ done/total",
        "[ADM-LST-01]\nInstance có task đã/không confirm",
        note="BR progress v2 — checklist-ba §7",
    ))
    c.append(case(
        "ADM-LST-07",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "ADMIN mở chi tiết checklist từ dòng danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Chọn dòng checklist cần xem\n"
        "4. Nhấn vào dòng hoặc thao tác mở chi tiết",
        "1. Chuyển sang màn [Chi tiết checklist]\n"
        "2. URL dạng /hrm/checklist/{instanceId}\n"
        "3. Hiển thị thông tin nhân viên, ngày bắt đầu, tiến độ",
        "[ADM-LST-01]",
    ))
    c.append(case(
        "ADM-LST-08",
        "[ADMIN] Danh sách checklist — /hrm/checklist",
        "Hiển thị fullName và accountName nhân viên trên danh sách (BR-13)",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Quan sát cột [Nhân viên] tại các dòng có dữ liệu",
        "1. Mỗi nhân viên hiển thị 2 dòng: fullName và accountName\n"
        "2. fullName = user.FullName; accountName = AccessControlProfileName ?? Username\n"
        "3. Không để trống employeeName",
        "[ADM-LST-01]",
        note="BR-13 — checklist-ba §5.5",
    ))

    # ── ADMIN — Tạo instance ────────────────────────────────────────────
    c.append(case(
        "ADM-INS-01",
        "[ADMIN] Tạo checklist instance — UC-02",
        "ADMIN tạo checklist — template ngẫu nhiên + NV Nguyễn Việt Hải",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhấn [Tạo checklist]\n"
        "4. Chọn template bất kỳ (Active)\n"
        "5. Ngày bắt đầu = hôm nay\n"
        "6. Cán bộ phụ trách = Quyền Phạm Năng\n"
        "7. Nhân viên = Nguyễn Việt Hải\n"
        "8. Nhấn [Tạo]\n"
        "9. Tìm kiếm [Nguyễn Việt Hải] trên danh sách",
        "1. Tạo instance thành công\n"
        "2. Danh sách sau tìm chỉ hiển thị nhân viên Nguyễn Việt Hải",
        "[ADM-LST-01]\nTemplate Active, nhân viên chưa có instance trùng (BR-06)",
        "CB: Quyền Phạm Năng · NV: Nguyễn Việt Hải · Ngày bắt đầu: hôm nay",
        note="UC-02, BR-12",
    ))
    c.append(case(
        "ADM-INS-02",
        "[ADMIN] Tạo checklist instance — UC-02",
        "Verify danh sách sau tạo — tìm Nguyễn Việt Hải (kết quả ADM-INS-01)",
        "1. Đã hoàn tất [ADM-INS-01]\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Tìm kiếm [Nguyễn Việt Hải]\n"
        "4. Quan sát kết quả bảng",
        "1. Danh sách sau tìm chỉ hiển thị nhân viên Nguyễn Việt Hải (≥1 dòng)",
        "[ADM-INS-01]",
        "Keyword: Nguyễn Việt Hải",
        note="Verify create → list",
    ))
    c.append(case(
        "ADM-INS-03",
        "[ADMIN] Tạo checklist instance — BR-06",
        "Không tạo duplicate instance cùng Template + Employee đang active",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhấn button [Tạo checklist]\n"
        "4. Chọn cùng template và nhân viên [Nguyễn Việt Hải] đã có instance active (sau ADM-INS-01)\n"
        "5. Nhấn button [Tạo/Lưu]",
        "1. Hệ thống báo lỗi validate — không tạo duplicate (BR-06)\n"
        "2. Không sinh instance mới",
        "[ADM-INS-01]",
        "Template + NV: lấy từ instance ADM-INS-01 (Nguyễn Việt Hải)",
        note="BR-06",
    ))

    # ── ADMIN — Chi tiết instance ─────────────────────────────────────────
    c.append(case(
        "ADM-DTL-01",
        "[ADMIN] Chi tiết checklist — /hrm/checklist/:id",
        "Tiến độ chi tiết sau NV xác nhận task (FE count)",
        "1. ADMIN tạo template mới (automationtestver{N}, 3 mục)\n"
        "2. ADMIN tạo checklist — CB [Quyền Phạm Năng], NV [TK Chuyên viên]\n"
        "3. EMPLOYEE mở chi tiết → bấm hết [Đúng hạn]\n"
        "4. ADMIN mở lại chi tiết instance có task đã confirm → kiểm tra done/total",
        "1. NV đã xác nhận hết → tiến độ chi tiết phải đúng N/N (3 mục → 3/3)\n"
        "2. Count 0/N sau khi NV confirm = Fail (FE chưa cập nhật)",
        "[ADM-LST-07]",
        note="FE count sau employee confirm",
    ))
    c.append(case(
        "ADM-DTL-02",
        "[ADMIN] Chi tiết checklist — /hrm/checklist/:id",
        "ADMIN xem nhật ký thay đổi checklist",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Chi tiết checklist] có log\n"
        "3. Nhấn button [Nhật ký]",
        "1. Modal/panel nhật ký hiển thị\n"
        "2. Có action, actorFullName, actorAccountName, thời gian\n"
        "3. Dữ liệu read-only từ checklist_log",
        "[ADM-DTL-01]",
    ))
    c.append(case(
        "ADM-DTL-03",
        "[ADMIN] Chi tiết checklist — BR-07 UC-06",
        "ADMIN hủy checklist instance (bắt buộc lý do)",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Chi tiết checklist] Status ≠ Cancelled\n"
        "3. Nhấn button [Hủy checklist]\n"
        "4. Nhập [Lý do hủy]: automationtestver{N}\n"
        "5. Nhấn button [Xác nhận] trên modal",
        "1. Instance chuyển Status = Cancelled (BR-07)\n"
        "2. CancelReason được lưu\n"
        "3. Notify OFFICER + EMPLOYEE liên quan",
        "[ADM-DTL-01]\nInstance có thể hủy",
        TEXT_INPUT_RULE,
        note="UC-06, BR-07",
    ))
    c.append(case(
        "ADM-DTL-04",
        "[ADMIN] Chi tiết checklist — /hrm/checklist/:id",
        "ADMIN quay lại danh sách từ chi tiết",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Nhấn button [Quay lại]",
        "1. Quay về màn [Danh sách checklist]\n"
        "2. Danh sách hiển thị bình thường",
        "[ADM-DTL-01]",
    ))
    c.append(case(
        "ADM-DTL-05",
        "[ADMIN] Chi tiết checklist — BR-13",
        "Hiển thị position và department trên chi tiết",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Quan sát khối thông tin nhân viên",
        "1. Hiển thị fullName + accountName\n"
        "2. Hiển thị position, department (JOIN bảng có sẵn)\n"
        "3. Officer trên task cũng có fullName + accountName",
        "[ADM-DTL-01]",
        note="BR-13, BR-14",
    ))

    # ── ADMIN — Template ──────────────────────────────────────────────────
    c.append(case(
        "ADM-TPL-01",
        "[ADMIN] Mẫu checklist template — /hrm/checklist/template",
        "ADMIN truy cập danh sách template",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Chọn menu [Mẫu Checklist]\n"
        "3. Truy cập màn hình [Mẫu checklist]",
        "1. Danh sách template hiển thị\n"
        "2. Có cột: Mã template, Tên template, Mô tả, Trạng thái, Ngày tạo, Chức năng\n"
        "3. Có button [Tạo template mới]",
        "",
        note="UC-01",
    ))
    c.append(case(
        "ADM-TPL-02",
        "[ADMIN] Mẫu checklist template — UC-01",
        "ADMIN tạo template mới",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Nhấn button [Tạo template mới]\n"
        "4. Điền dữ liệu:\n"
        "- Mã template: automationtestver{N}\n"
        "- Tên template: automationtestver{N}\n"
        "- Mô tả: automationtestver{N}\n"
        "5. Thêm section và task (DurationDays nhập số: 3, 7, 14...)\n"
        "6. Gán [Cán bộ mặc định] cho từng task nếu có\n"
        "7. Nhấn button [Lưu]",
        "1. Template tạo thành công\n"
        "2. DefaultOfficerId lưu per task (BR-12)\n"
        "3. IsActive = Active",
        "[ADM-TPL-01]",
        TEXT_INPUT_RULE,
    ))
    c.append(case(
        "ADM-TPL-03",
        "[ADMIN] Mẫu checklist template — verify sau create",
        "Sau tạo template — quay danh sách kiểm tra hiển thị",
        "1. Hoàn tất tạo template tại case [ADM-TPL-02]\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Nhập [Keyword] là mã hoặc tên template vừa tạo: automationtestver{N}\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Template vừa tạo xuất hiện trong danh sách\n"
        "2. Đúng mã, tên, trạng thái Active",
        "[ADM-TPL-02]",
        "Keyword = automationtestver{N} vừa tạo",
        note="Verify create → list",
    ))
    c.append(case(
        "ADM-TPL-04",
        "[ADMIN] Mẫu checklist template",
        "ADMIN tìm kiếm template theo Keyword",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Nhập [Keyword] vào ô tìm kiếm: tuyendung\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Danh sách lọc theo Keyword\n"
        "2. Chỉ hiển thị template khớp",
        "[ADM-TPL-01]",
    ))
    c.append(case(
        "ADM-TPL-04B",
        "[ADMIN] Mẫu checklist template",
        "ADMIN tìm kiếm template — keyword có khoảng trắng đầu",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Nhập [Keyword] vào ô tìm kiếm: [space]tuyendung (khoảng trắng + tuyendung)\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Danh sách lọc theo Keyword (FE trim/normalize space đầu)\n"
        "2. Vẫn hiển thị template Tuyển dụng khớp",
        "[ADM-TPL-01]",
        note="Keyword: ' tuyendung'",
    ))
    c.append(case(
        "ADM-TPL-05",
        "[ADMIN] Mẫu checklist template",
        "ADMIN bật/tắt trạng thái Active template",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Chọn dòng template cần đổi trạng thái\n"
        "4. Nhấn toggle [Trạng thái] Active/Off",
        "1. Trạng thái template đổi qua PATCH /toggleActive\n"
        "2. UI phản ánh Active hoặc Off",
        "[ADM-TPL-01]",
    ))
    c.append(case(
        "ADM-TPL-06",
        "[ADMIN] Mẫu checklist template",
        "ADMIN xem chi tiết template",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Chọn dòng template\n"
        "4. Nhấn icon [Xem] tại cột [Chức năng]",
        "1. Mở màn/xem chi tiết template\n"
        "2. Hiển thị sections, tasks, DefaultOfficerId",
        "[ADM-TPL-01]",
    ))
    c.append(case(
        "ADM-TPL-07",
        "[ADMIN] Mẫu checklist template — BR-08",
        "ADMIN sửa template khi không có instance active",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Chọn template không có instance Status ∈ {0,1,3}\n"
        "4. Nhấn icon [Sửa] tại cột [Chức năng]\n"
        "5. Sửa [Tên template] thành automationtestver{N}\n"
        "6. Nhấn button [Lưu]",
        "1. Cập nhật thành công (BR-08)\n"
        "2. Thay đổi được lưu vào DB",
        "[ADM-TPL-01]\nTemplate không có instance active",
        TEXT_INPUT_RULE,
        note="BR-08",
    ))
    c.append(case(
        "ADM-TPL-08",
        "[ADMIN] Mẫu checklist template — verify sau edit",
        "Sau sửa template — quay danh sách kiểm tra tên mới",
        "1. Hoàn tất sửa template tại case [ADM-TPL-07]\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Nhập [Keyword]: automationtestver{N} vừa sửa\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Template hiển thị tên mới trong danh sách\n"
        "2. Dữ liệu khớp với lần sửa",
        "[ADM-TPL-07]",
        note="Verify edit → list",
    ))

    # ── OFFICER — Danh sách ─────────────────────────────────────────────
    c.append(case(
        "OFF-LST-01",
        "[OFFICER] Danh sách checklist — BR-10",
        "OFFICER chỉ thấy checklist có task được giao",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Chọn menu [Checklist]\n"
        "3. Truy cập màn hình [Danh sách checklist]",
        "1. Danh sách chỉ instance có task AssignedOfficerId = OFFICER hiện tại (BR-10)\n"
        "2. Không thấy instance không liên quan\n"
        "3. Không truy cập được template admin-only",
        "OFFICER có task được giao trong ít nhất 1 instance",
    ))
    c.append(case(
        "OFF-LST-02",
        "[OFFICER] Danh sách checklist",
        "OFFICER tìm kiếm checklist theo Keyword",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhập [Keyword] vào ô tìm kiếm\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Kết quả lọc trong phạm vi quyền OFFICER\n"
        "2. Chỉ record liên quan task của OFFICER",
        "[OFF-LST-01]",
    ))
    c.append(case(
        "OFF-LST-03",
        "[OFFICER] Danh sách checklist",
        "OFFICER lọc checklist theo khoảng ngày",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Chọn khoảng ngày trên lịch\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Danh sách lọc theo FromDate–ToDate\n"
        "2. Vẫn trong phạm vi quyền OFFICER",
        "[OFF-LST-01]",
    ))
    c.append(case(
        "OFF-LST-04",
        "[OFFICER] Danh sách checklist",
        "OFFICER làm mới danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhấn button [Làm mới]",
        "1. Danh sách tải lại thành công",
        "[OFF-LST-01]",
    ))

    # ── OFFICER — Xác nhận task ──────────────────────────────────────────
    c.append(case(
        "OFF-CFM-01",
        "[OFFICER] Xác nhận task — UC-03",
        "OFFICER mở chi tiết checklist có task được giao",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Chọn instance có task AssignedOfficerId = mình\n"
        "4. Truy cập màn hình [Chi tiết checklist]",
        "1. Hiển thị danh sách task theo section\n"
        "2. Task được giao có thể thao tác Xác nhận / Đổi cán bộ\n"
        "3. Có button [Xác nhận], [Đổi cán bộ] trên task",
        "[OFF-LST-01]\nInstance có task pending cho OFFICER",
        note="UC-03",
    ))
    c.append(case(
        "OFF-CFM-02",
        "[OFFICER] Xác nhận task — BR-01 UC-03",
        "OFFICER xác nhận task đúng hạn (không cần employee confirm trước)",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Chọn task chưa confirm, Deadline chưa qua\n"
        "4. Nhấn button [Xác nhận]\n"
        "5. Nhập [Ghi chú minh chứng]: automationtestver{N}\n"
        "6. Chụp ảnh minh chứng và lưu\n"
        "7. Nhấn button [Xác nhận] trên modal",
        "1. OfficerStatus = Confirmed (1) — BR-01 song song\n"
        "2. EmployeeStatus vẫn có thể Pending — không bắt buộc thứ tự\n"
        "3. Task chưa done cho đến khi cả 2 bên ∈ {1,3}\n"
        "4. Có ảnh minh chứng trong ô [Minh chứng]",
        "[OFF-CFM-01]\nTask trước Deadline",
        TEXT_INPUT_RULE,
        note="BR-01, UC-03 — chụp ảnh khi chạy automation",
    ))
    c.append(case(
        "OFF-CFM-03",
        "[OFFICER] Xác nhận task — BR-03",
        "OFFICER xác nhận task muộn — bắt buộc lý do",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Chọn task quá Deadline, OfficerStatus = Pending\n"
        "4. Nhấn button [Xác nhận]\n"
        "5. Nhập [Lý do muộn]: automationtestver{N}\n"
        "6. Nhấn button [Xác nhận]",
        "1. OfficerStatus = Late (3)\n"
        "2. OfficerLateReason bắt buộc (BR-03)\n"
        "3. Ghi log OfficerConfirmLate",
        "[OFF-CFM-01]\nTask quá Deadline",
        TEXT_INPUT_RULE,
        note="BR-03",
    ))
    c.append(case(
        "OFF-CFM-04",
        "[OFFICER] Đổi cán bộ — UC-05 BR-04",
        "OFFICER đổi cán bộ phụ trách task chưa confirm",
        "1. Đăng nhập hệ thống bằng tài khoản OFFICER\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Chọn task có OfficerStatus ∈ {0, 2}\n"
        "4. Nhấn button [Đổi cán bộ]\n"
        "5. Chọn cán bộ mới\n"
        "6. Nhấn button [Lưu]",
        "1. AssignedOfficerId đổi thành công (BR-04)\n"
        "2. Ghi log ChangeOfficer\n"
        "3. Notify OFFICER mới",
        "[OFF-CFM-01]\nTask chưa officer confirm",
        note="UC-05, BR-04",
    ))
    c.append(case(
        "OFF-CFM-05",
        "[OFFICER] Undo xác nhận — BR-02",
        "OFFICER undo xác nhận trong 60 phút khi employee chưa confirm",
        "1. Hoàn tất officer confirm tại case [OFF-CFM-02]\n"
        "2. Đảm bảo EmployeeStatus task đó = 0\n"
        "3. Trong vòng 60 phút, nhấn button [Hoàn tác] / Undo\n"
        "4. Xác nhận undo",
        "1. OfficerStatus = Undone (2) hoặc về Pending\n"
        "2. canOfficerUndo = true khi trong 60' và employee chưa confirm (BR-02)\n"
        "3. Sau employee confirm → không undo được",
        "[OFF-CFM-02]\nEmployeeStatus = 0, trong 60 phút",
        note="BR-02",
    ))

    # ── EMPLOYEE — Danh sách ─────────────────────────────────────────────
    c.append(case(
        "EMP-LST-01",
        "[EMPLOYEE] Danh sách checklist — BR-10",
        "EMPLOYEE chỉ thấy checklist của bản thân",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Chọn menu [Checklist]\n"
        "3. Truy cập màn hình [Danh sách checklist]",
        "1. Chỉ instance có EmployeeId = user hiện tại (BR-10)\n"
        "2. Không thấy checklist nhân viên khác",
        "EMPLOYEE có ít nhất 1 instance",
    ))
    c.append(case(
        "EMP-LST-02",
        "[EMPLOYEE] Danh sách checklist",
        "EMPLOYEE tìm kiếm checklist",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Nhập [Keyword] vào ô tìm kiếm\n"
        "4. Nhấn button [Tìm kiếm]",
        "1. Kết quả trong phạm vi instance của EMPLOYEE",
        "[EMP-LST-01]",
    ))
    c.append(case(
        "EMP-LST-03",
        "[EMPLOYEE] Danh sách checklist",
        "Hiển thị badge overdue trên danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Quan sát dòng có task quá hạn",
        "1. Hiển thị badge/số overdueTaskCount > 0\n"
        "2. Instance không overdue không hiển thị badge (hoặc = 0)",
        "[EMP-LST-01]\nInstance có task overdue",
        note="overdue badge — explore sample: 2 trễ",
    ))
    c.append(case(
        "EMP-LST-04",
        "[EMPLOYEE] Danh sách checklist",
        "EMPLOYEE mở chi tiết checklist từ danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Danh sách checklist]\n"
        "3. Chọn dòng checklist của bản thân\n"
        "4. Truy cập màn hình [Chi tiết checklist]",
        "1. Mở đúng instance của EMPLOYEE\n"
        "2. Hiển thị task cần xác nhận",
        "[EMP-LST-01]",
    ))

    # ── EMPLOYEE — Xác nhận ─────────────────────────────────────────────
    c.append(case(
        "EMP-CFM-01",
        "[EMPLOYEE] Xác nhận task — BR-01 UC-04",
        "EMPLOYEE xác nhận task không cần officer confirm trước",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Chọn task EmployeeStatus = Pending, OfficerStatus vẫn = 0\n"
        "4. Nhấn button [Xác nhận]\n"
        "5. Nhập [Ghi chú]: automationtestver{N}\n"
        "6. Chụp ảnh minh chứng\n"
        "7. Nhấn button [Xác nhận]",
        "1. Employee confirm thành công dù officer chưa confirm (BR-01)\n"
        "2. EmployeeStatus = Confirmed (1)\n"
        "3. Ảnh minh chứng lưu vào ô [Minh chứng]",
        "[EMP-LST-04]\nTask employee pending, officer chưa confirm",
        TEXT_INPUT_RULE,
        note="BR-01, UC-04",
    ))
    c.append(case(
        "EMP-CFM-02",
        "[EMPLOYEE] Xác nhận task — BR-03",
        "EMPLOYEE xác nhận muộn — bắt buộc lý do",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Chọn task quá Deadline\n"
        "4. Nhấn button [Xác nhận]\n"
        "5. Nhập [Lý do muộn]: automationtestver{N}\n"
        "6. Nhấn button [Xác nhận]",
        "1. EmployeeStatus = Late (3)\n"
        "2. EmployeeLateReason bắt buộc (BR-03)",
        "[EMP-LST-04]\nTask quá Deadline",
        TEXT_INPUT_RULE,
        note="BR-03",
    ))
    c.append(case(
        "EMP-CFM-03",
        "[EMPLOYEE] Chi tiết checklist",
        "EMPLOYEE xem nhật ký và quay lại danh sách",
        "1. Đăng nhập hệ thống bằng tài khoản EMPLOYEE\n"
        "2. Truy cập màn hình [Chi tiết checklist]\n"
        "3. Nhấn button [Nhật ký]\n"
        "4. Đóng nhật ký\n"
        "5. Nhấn button [Quay lại]",
        "1. Nhật ký hiển thị đúng\n"
        "2. Quay về [Danh sách checklist] thành công",
        "[EMP-LST-04]",
    ))

    # ── Business Rules — luồng chéo ───────────────────────────────────────
    c.append(case(
        "BR-TPL-01",
        "[BR] Template Active/Off",
        "Template Tuyển dụng OFF — không hiện trong dropdown Tạo checklist",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Tìm dòng template [Tuyển dụng]\n"
        "4. Nhấn toggle [Trạng thái] chuyển sang Off\n"
        "5. Truy cập màn hình [Danh sách checklist]\n"
        "6. Nhấn button [Tạo checklist]\n"
        "7. Nhấn dropdown [Template]\n"
        "8. Quan sát danh sách lựa chọn",
        "1. Dropdown Template không chứa [Tuyển dụng]\n"
        "2. Các template Active khác vẫn hiển thị bình thường",
        "[ADM-TPL-01]\nTemplate: Tuyển dụng (mã tuyendung)",
        "Template: Tuyển dụng",
        note="BR template IsActive — workflow/BR/BR-TPL-01.md",
    ))
    c.append(case(
        "BR-01",
        "[BR] Xác nhận song song",
        "Officer và Employee xác nhận độc lập — không thứ tự",
        "1. Chuẩn bị instance có task pending cả 2 bên\n"
        "2. Đăng nhập EMPLOYEE — xác nhận task trước (case [EMP-CFM-01])\n"
        "3. Đăng xuất — đăng nhập OFFICER — xác nhận cùng task sau (case [OFF-CFM-02])\n"
        "4. Quan sát trạng thái task và instance",
        "1. Cả 2 confirm thành công không phụ thuộc thứ tự (BR-01)\n"
        "2. Task done khi Officer ∈ {1,3} AND Employee ∈ {1,3}",
        "[EMP-CFM-01], [OFF-CFM-02]",
        note="BR-01 — checklist-ba §2",
    ))
    c.append(case(
        "BR-05",
        "[BR] Auto complete instance",
        "Instance tự chuyển Completed khi mọi task done",
        "1. Chuẩn bị instance gần hoàn thành — còn 1 task chưa done\n"
        "2. OFFICER và EMPLOYEE xác nhận task cuối\n"
        "3. ADMIN mở [Danh sách checklist] kiểm tra trạng thái",
        "1. Mọi task done → Instance Status = Completed (2) (BR-05)\n"
        "2. Notify ADMIN + EMPLOYEE\n"
        "3. progressPercent = 100%",
        "[OFF-CFM-02], [EMP-CFM-01]",
        note="BR-05",
    ))
    c.append(case(
        "BR-08",
        "[BR] Sửa template",
        "Không sửa template khi còn instance active",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Truy cập màn hình [Mẫu checklist]\n"
        "3. Chọn template đang có instance Status ∈ {Pending, InProgress, Overdue}\n"
        "4. Nhấn icon [Sửa]",
        "1. Hệ thống chặn sửa hoặc báo lỗi (BR-08)\n"
        "2. Template không bị thay đổi",
        "Template có instance active",
        note="BR-08",
    ))
    c.append(case(
        "BR-09",
        "[BR] Deadline calendar",
        "Deadline task = StartDate + DurationDays (ngày calendar)",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Tạo instance với StartDate và template có DurationDays = 7\n"
        "3. Mở [Chi tiết checklist] kiểm tra Deadline từng task",
        "1. Deadline = StartDate + 7 ngày calendar (BR-09)\n"
        "2. Không trừ T7/CN",
        "[ADM-INS-01]\nTemplate task DurationDays = 7",
        "DurationDays: 7 (số)",
        note="BR-09",
    ))
    c.append(case(
        "BR-12",
        "[BR] Officer mặc định từ template",
        "AssignedOfficerId tự áp từ DefaultOfficerId khi tạo instance",
        "1. Đăng nhập hệ thống bằng tài khoản ADMIN\n"
        "2. Tạo/sử dụng template có DefaultOfficerId trên từng task\n"
        "3. Tạo instance mới từ template đó\n"
        "4. Mở [Chi tiết checklist] kiểm tra AssignedOfficerId",
        "1. Mỗi task_item.AssignedOfficerId = template_task.DefaultOfficerId (BR-12)\n"
        "2. Nếu DefaultOfficerId null → dùng assignedOfficerId request",
        "[ADM-TPL-02], [ADM-INS-01]",
        note="BR-12",
    ))

    return c


def main() -> None:
    cases = apply_conditions(build_cases())
    data = {
        "moduleCode": "Checklist Nhân sự",
        "requirement": (
            "Verify module Checklist Nhân sự v2 — redesign từ explore "
            f"{RUN_ID} + checklist-ba.md. Chia theo role, ưu tiên luồng nghiệp vụ + BR."
        ),
        "tester": "HaiNV_TE_FU",
        "cases": cases,
        "sourceExploreRun": RUN_ID,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
    }
    saved = save_testcases(data)
    out = ROOT / "data" / "testcases.json"
    print(f"Generated {len(saved['cases'])} test cases -> {out}")
    print(f"Stats: {saved['stats']}")


if __name__ == "__main__":
    main()
