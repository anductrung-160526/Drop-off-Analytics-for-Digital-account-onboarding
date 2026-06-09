"""
tools.py
--------
Các "công cụ" (tool) cho phần Agentic AI.

Ý tưởng: agent tự quyết định khi nào dùng RAG (tra tài liệu) và khi nào
gọi một hàm tính toán. Đây là điểm chạm từ khóa "AI Agents" trong JD.
"""

from langchain.agents import tool


@tool
def tinh_phi_chuyen_khoan(so_tien: float) -> str:
    """Tính phí chuyển khoản liên ngân hàng.
    Quy tắc giả lập: phí = 0.02% số tiền, tối thiểu 11.000đ.
    Dùng khi khách hỏi phí chuyển một số tiền cụ thể."""
    phi = max(so_tien * 0.0002, 11000)
    return f"Phí chuyển {so_tien:,.0f}đ là {phi:,.0f}đ."


@tool
def tinh_lai_tiet_kiem(so_tien: float, lai_suat_nam: float, so_thang: int) -> str:
    """Tính tiền lãi gửi tiết kiệm có kỳ hạn (lãi đơn).
    so_tien: số tiền gửi (đồng).
    lai_suat_nam: lãi suất %/năm (ví dụ 5.5).
    so_thang: số tháng gửi.
    Dùng khi khách muốn ước tính lãi cho một khoản gửi cụ thể."""
    lai = so_tien * (lai_suat_nam / 100) * (so_thang / 12)
    tong = so_tien + lai
    return (
        f"Gửi {so_tien:,.0f}đ, lãi suất {lai_suat_nam}%/năm trong {so_thang} tháng:\n"
        f"- Tiền lãi: {lai:,.0f}đ\n"
        f"- Tổng nhận: {tong:,.0f}đ"
    )


# Danh sách tool để agent sử dụng
ALL_TOOLS = [tinh_phi_chuyen_khoan, tinh_lai_tiet_kiem]
