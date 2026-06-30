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
        "passCondition": "Sau ADMIN tạo template [automationtestver{N}_autotestasignees] + checklist (NV TK Chuyên Viên), OFFICER đăng nhập tìm đúng tên → có ≥1 dòng.",
        "failCondition": "Không tạo được template/checklist (ADMIN) hoặc OFFICER không tìm thấy checklist vừa tạo.",
    },
    "OFF-LST-02": {
        "passCondition": "OFFICER tìm keyword checklist OFF-LST-01 (automationtestver{N}_autotestasignees) → có ≥1 dòng trong phạm vi quyền.",
        "failCondition": "Không tìm thấy record OFF-LST-01 — cần chạy OFF-LST-01 trước.",
    },
    "OFF-LST-03": {
        "passCondition": "OFFICER lọc 26/06/2026–29/06/2026 → mọi dòng có Từ ngày / Đến ngày nằm trọn trong khoảng (boundary pass).",
        "failCondition": "Có ≥1 dòng vượt biên — vd. Đến ngày 30/06/2026 > 29/06/2026 khi lọc đến 29/06 (BUG BE overlap).",
    },
    "OFF-LST-04": {
        "passCondition": "Nút làm mới (reload) tải lại danh sách checklist.",
        "failCondition": "Không bấm được nút làm mới.",
    },
    "OFF-CFM-01": {
        "passCondition": "OFFICER (trưởng phòng) tự tạo template + checklist → mở chi tiết → có task + nút [Đúng hạn]/Xác nhận hoặc [Đổi CB].",
        "failCondition": "OFFICER không tạo được template/checklist / không mở chi tiết / không thấy thao tác task.",
    },
    "OFF-CFM-02": {
        "passCondition": "OFFICER [Đúng hạn] task 1 + EMPLOYEE [Đúng hạn] task 2 — cả hai toast thành công, modal đóng (BR-01).",
        "failCondition": "Toast lỗi khi xác nhận (vd. không có quyền) / modal không đóng / không thấy nút Đúng hạn.",
    },
    "OFF-CFM-03": {
        "passCondition": "Task quá hạn: bấm [Muộn] → nhập automationtestver{N} → toast thành công (BR-03).",
        "failCondition": "Không có task overdue / toast lỗi / modal không đóng.",
    },
    "OFF-CFM-04": {
        "passCondition": "Task 1 [Muộn] xong → task 2 [Đổi CB] → chọn cán bộ mới ngẫu nhiên → [Lưu] toast thành công (BR-04).",
        "failCondition": "Không tạo được checklist overdue / không [Muộn] task 1 / không thấy [Đổi CB] / toast lỗi khi Lưu.",
    },
    "OFF-CFM-05": {
        "passCondition": "Task 1 [Muộn] xong → [Hoàn tác] → xác nhận — task về chờ xử lý, trong 60' employee chưa confirm (BR-02).",
        "failCondition": "Không tạo được checklist / không [Muộn] / không thấy [Hoàn tác] / toast lỗi khi undo.",
    },
    "OFF-CFM-06": {
        "passCondition": "OFFICER lọc [Quá hạn] → có dòng có chữ «trễ» hoặc tiến độ chưa xong (0/2, 1/3, 2/3…).",
        "failCondition": "Không lọc được [Quá hạn] / 0 dòng / có dòng nhưng không thấy trễ hoặc tiến độ chưa hoàn thành.",
    },
    "EMP-LST-01": {
        "passCondition": "ADMIN template → OFF [Tạo checklist] (hôm nay, TK Chuyên Viên) → logout → EMP đăng nhập thấy đúng checklist (BR-10).",
        "failCondition": "OFF không tạo được checklist / EMP không thấy checklist OFF vừa tạo.",
    },
    "EMP-LST-02": {
        "passCondition": "EMPLOYEE đăng nhập → search keyword checklist (từ EMP-LST-01 hoặc prep OFF) → có kết quả.",
        "failCondition": "Không có dữ liệu checklist / không tìm thấy khi search.",
    },
    "EMP-LST-03": {
        "passCondition": "Cuộn bảng đến dòng có chữ «trễ» → chụp minh chứng đúng vị trí badge (EMP/OFF/ADMIN).",
        "failCondition": "Cuộn hết bảng/phân trang vẫn không thấy chữ «trễ».",
    },
    "EMP-LST-04": {
        "passCondition": "Mở dòng danh sách → chi tiết checklist; URL /hrm/checklist/{id}.",
        "failCondition": "Không có checklist / không mở được chi tiết.",
    },
    "EMP-CFM-01": {
        "passCondition": "OFF tạo checklist (hôm nay) → EMP [Đúng hạn] + automationtestver{N} → toast thành công trước officer (BR-01).",
        "failCondition": "OFF không tạo checklist / không mở chi tiết / không thấy [Đúng hạn] / toast lỗi.",
    },
    "EMP-CFM-02": {
        "passCondition": "OFF tạo checklist quá hạn → EMP [Muộn] + automationtestver{N} → toast thành công (BR-03).",
        "failCondition": "Không tạo overdue / không thấy [Muộn] / toast lỗi khi xác nhận.",
    },
    "EMP-CFM-03": {
        "passCondition": "Có marker EMP-CFM-02 hoặc tự [Muộn] → [Nhật ký] có log → đóng → [Quay lại] danh sách.",
        "failCondition": "Không tạo/xác nhận được / nhật ký trống / Quay lại thất bại.",
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
