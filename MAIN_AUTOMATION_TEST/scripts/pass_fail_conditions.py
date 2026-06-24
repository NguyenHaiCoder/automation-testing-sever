# -*- coding: utf-8 -*-
"""
Điều kiện Pass/Fail cho automation — đối chiếu workflow + run case-runs.
Bỏ qua ADM-LST-01..05 (đã chốt) và toàn bộ BR-*.
"""
from __future__ import annotations

SKIP_IDS = frozenset(
    {
        "ADM-LST-01",
        "ADM-LST-02",
        "ADM-LST-03",
        "ADM-LST-04",
        "ADM-LST-05",
        "BR-TPL-01",
        "BR-01",
        "BR-05",
        "BR-08",
        "BR-09",
        "BR-12",
    }
)

CONDITIONS: dict[str, dict[str, str]] = {
    "ADM-LST-06": {
        "passCondition": "Cột [Tiến độ] có ít nhất 1 dòng hiển thị dạng done/total (vd: 0/3, 2/3).",
        "failCondition": "Không thấy định dạng done/total trong cột Tiến độ.",
    },
    "ADM-LST-07": {
        "passCondition": "Bấm dòng danh sách → chuyển màn chi tiết; URL dạng /hrm/checklist/{instanceId}.",
        "failCondition": "Không có dòng để mở / không mở được chi tiết / URL không phải trang chi tiết.",
    },
    "ADM-LST-08": {
        "passCondition": "Mỗi dòng trong cột [Nhân viên] hiển thị 2 dòng: fullName (dòng 1) + accountName (dòng 2); cả hai không trống (BR-13).",
        "failCondition": "Có dòng thiếu fullName/accountName hoặc cột Nhân viên chỉ 1 dòng / để trống employeeName.",
    },
    "ADM-INS-01": {
        "passCondition": "Tạo checklist xong → tìm [Nguyễn Việt Hải] trên danh sách → bảng chỉ hiển thị nhân viên đó (≥1 dòng).",
        "failCondition": "Không tạo được / báo trùng BR-06 / sau tìm không có dòng / có nhân viên khác ngoài Nguyễn Việt Hải.",
    },
    "ADM-INS-02": {
        "passCondition": "Tìm [Nguyễn Việt Hải] trên danh sách → có ≥1 dòng hiển thị nhân viên đó (kết quả ADM-INS-01).",
        "failCondition": "Không tìm thấy [Nguyễn Việt Hải] sau tìm kiếm — cần chạy ADM-INS-01 trước.",
    },
    "ADM-INS-03": {
        "passCondition": "BR-06 chặn (số dòng không đổi) + toast/modal có [Trùng] hoặc [đã có] — không được hiện [Tạo thành công].",
        "failCondition": "Vẫn tạo instance mới / hoặc FE sai toast (báo thành công dù BR-06 chặn) / thiếu thông báo Trùng–đã có.",
    },
    "ADM-DTL-01": {
        "passCondition": "NV xác nhận hết task → ADMIN chi tiết hiển thị đúng N/N (3 mục template → 3/3).",
        "failCondition": "Count vẫn 0/N hoặc khác N/N sau khi NV confirm hết / không hoàn tất luồng tạo–logout–confirm.",
    },
    "ADM-DTL-02": {
        "passCondition": "Bấm [Nhật ký] → modal có ít nhất 1 dòng log kèm ngày giờ (dd/mm HH:mm).",
        "failCondition": "Không mở được chi tiết / không mở được Nhật ký / nhật ký trống hoặc thiếu ngày giờ.",
    },
    "ADM-DTL-03": {
        "passCondition": "Flow [Hủy checklist] → nhập lý do automationtestver{N} → Xác nhận — không có toast lỗi.",
        "failCondition": "Toast [Có lỗi xảy ra khi hủy checklist!] / không thấy nút Hủy / không mở được chi tiết chưa hủy.",
    },
    "ADM-DTL-04": {
        "passCondition": "Nút [Quay lại] từ chi tiết → về màn [Danh sách checklist].",
        "failCondition": "Không mở được chi tiết / nút Quay lại không hoạt động.",
    },
    "ADM-DTL-05": {
        "passCondition": "Khối nhân viên trên chi tiết có fullName + accountName và thông tin chức vụ/đơn vị (BR-13).",
        "failCondition": "Thiếu thông tin nhân viên trên màn chi tiết.",
    },
    "ADM-TPL-01": {
        "passCondition": "Danh sách template hiển thị đủ cột (Mã, Tên, Mô tả, Trạng thái…) và có nút [Tạo template mới].",
        "failCondition": "Không thấy bảng template / thiếu nút tạo mới.",
    },
    "ADM-TPL-02": {
        "passCondition": "Tạo template automationtestver{N} + Lưu → tìm kiếm đúng keyword đó thấy trên danh sách (Active).",
        "failCondition": "Không Lưu được / tạo xong nhưng không tìm thấy đúng automationtestver{N} trên danh sách.",
    },
    "ADM-TPL-03": {
        "passCondition": "Tìm keyword đúng automationtestver{N} (từ ADM-TPL-02) → có dòng khớp mã/tên và Active.",
        "failCondition": "Không tìm thấy đúng template ADM-TPL-02 — cần chạy ADM-TPL-02 trước.",
    },
    "ADM-TPL-04": {
        "passCondition": "Tìm keyword [tuyendung] → bảng có template Tuyển dụng.",
        "failCondition": "Không thấy template Tuyển dụng sau tìm kiếm.",
    },
    "ADM-TPL-04B": {
        "passCondition": "Tìm keyword [ tuyendung] (khoảng trắng + tuyendung) → bảng vẫn có template Tuyển dụng.",
        "failCondition": "Keyword có space đầu không trả kết quả / không thấy template Tuyển dụng.",
    },
    "ADM-TPL-05": {
        "passCondition": "Toggle Active/Off trên template Tuyển dụng đổi trạng thái (script khôi phục lại sau khi test).",
        "failCondition": "Toggle không đổi trạng thái switch.",
    },
    "ADM-TPL-06": {
        "passCondition": "Icon [Xem] mở được màn/xem chi tiết template.",
        "failCondition": "Không bấm được icon Xem / không mở chi tiết.",
    },
    "ADM-TPL-07": {
        "passCondition": "Mở form Sửa template + đổi tên automationtestver{N} + Lưu thành công.",
        "failCondition": "Không mở được form sửa / không Lưu được.",
    },
    "ADM-TPL-08": {
        "passCondition": "Tìm đúng keyword automationtestver{N} (từ ADM-TPL-07) → template hiển thị trên danh sách.",
        "failCondition": "Không tìm thấy đúng tên sau sửa — cần chạy ADM-TPL-07 trước.",
    },
    "OFF-LST-01": {
        "passCondition": "Sau ADMIN tạo template [automationtestver{N}-autotestasignees] + checklist (NV TK Chuyên Viên), OFFICER đăng nhập tìm đúng tên → có ≥1 dòng.",
        "failCondition": "Không tạo được template/checklist (ADMIN) hoặc OFFICER không tìm thấy checklist vừa tạo.",
    },
    "OFF-LST-02": {
        "passCondition": "Nhập keyword [test] + Tìm kiếm → danh sách cập nhật trong phạm vi quyền OFFICER.",
        "failCondition": "Không vào được danh sách / không thực hiện được tìm kiếm.",
    },
    "OFF-LST-03": {
        "passCondition": "Chọn khoảng ngày trên date picker → danh sách lọc được (dropdown tự áp dụng hoặc sau Tìm kiếm).",
        "failCondition": "Không mở/chọn được lịch khoảng ngày.",
    },
    "OFF-LST-04": {
        "passCondition": "Nút làm mới (reload) tải lại danh sách checklist.",
        "failCondition": "Không bấm được nút làm mới.",
    },
    "OFF-CFM-01": {
        "passCondition": "Màn chi tiết có task với nút [Đúng hạn]/Xác nhận hoặc [Đổi CB]/Đổi cán bộ.",
        "failCondition": "OFFICER không có instance để mở / không thấy thao tác task trên chi tiết.",
    },
    "OFF-CFM-02": {
        "passCondition": "Bấm [Đúng hạn] → nhập automationtestver{N} → Xác nhận modal thành công (BR-01).",
        "failCondition": "Không có chi tiết / không thấy nút Đúng hạn.",
    },
    "OFF-CFM-03": {
        "passCondition": "Task quá hạn: bấm [Muộn] → nhập lý do → Xác nhận (BR-03).",
        "failCondition": "Không có task overdue (không thấy nút Muộn).",
    },
    "OFF-CFM-04": {
        "passCondition": "Flow [Đổi cán bộ] mở modal, chọn cán bộ mới và Lưu (BR-04).",
        "failCondition": "Không thấy nút Đổi cán bộ / không hoàn tất flow.",
    },
    "OFF-CFM-05": {
        "passCondition": "Nút [Hoàn tác] undo xác nhận officer trong cửa sổ 60 phút (BR-02).",
        "failCondition": "Không thấy nút Hoàn tác — cần officer đã confirm gần đây.",
    },
    "EMP-LST-01": {
        "passCondition": "EMPLOYEE thấy ≥1 dòng checklist của bản thân (BR-10).",
        "failCondition": "Không thấy bảng / 0 dòng checklist của employee đăng nhập.",
    },
    "EMP-LST-02": {
        "passCondition": "Tìm keyword [test] trong phạm vi checklist của EMPLOYEE.",
        "failCondition": "Không vào được danh sách / không tìm kiếm được.",
    },
    "EMP-LST-03": {
        "passCondition": "Danh sách hiển thị badge/tag overdue (task trễ) trên ít nhất 1 dòng.",
        "failCondition": "Không thấy badge overdue — cần instance có task quá hạn.",
    },
    "EMP-LST-04": {
        "passCondition": "Mở dòng danh sách → chi tiết checklist; URL /hrm/checklist/{id}.",
        "failCondition": "Không có checklist / không mở được chi tiết.",
    },
    "EMP-CFM-01": {
        "passCondition": "EMPLOYEE bấm [Đúng hạn] → nhập automationtestver{N} → Xác nhận (BR-01, không cần officer trước).",
        "failCondition": "Không có chi tiết / không thấy nút Đúng hạn.",
    },
    "EMP-CFM-02": {
        "passCondition": "Task quá hạn: [Muộn] → lý do → Xác nhận (BR-03).",
        "failCondition": "Không có task overdue.",
    },
    "EMP-CFM-03": {
        "passCondition": "Mở [Nhật ký] từ chi tiết + [Quay lại] về danh sách.",
        "failCondition": "Không mở Nhật ký / Quay lại thất bại.",
    },
}


def apply_conditions(cases: list[dict]) -> list[dict]:
    for item in cases:
        cid = item.get("id", "")
        if cid in SKIP_IDS or cid not in CONDITIONS:
            continue
        item["passCondition"] = CONDITIONS[cid]["passCondition"]
        item["failCondition"] = CONDITIONS[cid]["failCondition"]
    return cases


def patch_testcases_json(path) -> int:
    import json
    from pathlib import Path

    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    apply_conditions(data["cases"])
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sum(1 for c in data["cases"] if c.get("passCondition"))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "data" / "testcases.json"
    n = patch_testcases_json(target)
    print(f"Da them passCondition/failCondition cho {n} case")
