"""
app.py
------
Giao diện web demo bằng Streamlit.

Chạy:
    streamlit run app.py
"""

import streamlit as st

from rag_chain import build_qa_chain, ask

st.set_page_config(page_title="Trợ lý hỏi đáp ngân hàng", page_icon="🏦")
st.title("🏦 Trợ lý hỏi đáp tài liệu sản phẩm ngân hàng")
st.caption("Demo RAG: trả lời dựa trên tài liệu nội bộ, có trích dẫn nguồn.")


# @st.cache_resource: chỉ tải mô hình/index MỘT lần, không tải lại mỗi câu hỏi.
@st.cache_resource(show_spinner="Đang khởi tạo trợ lý...")
def get_chain():
    return build_qa_chain()


try:
    chain = get_chain()
except Exception as e:
    st.error(f"Lỗi khởi tạo: {e}")
    st.info("Kiểm tra: đã chạy `python ingest.py` chưa? Đã đặt OPENAI_API_KEY chưa?")
    st.stop()


# Gợi ý câu hỏi mẫu để người dùng bấm thử
st.markdown("**Câu hỏi gợi ý:**")
cols = st.columns(3)
samples = [
    "Lãi suất tiết kiệm online kỳ hạn 6 tháng là bao nhiêu?",
    "Phí chuyển khoản liên ngân hàng tính thế nào?",
    "Điều kiện mở tài khoản tiết kiệm số?",
]
for col, s in zip(cols, samples):
    if col.button(s, use_container_width=True):
        st.session_state["query"] = s

query = st.text_input(
    "Nhập câu hỏi của bạn:",
    value=st.session_state.get("query", ""),
)

if query:
    with st.spinner("Đang tìm câu trả lời..."):
        answer, sources = ask(chain, query)

    st.markdown("### Trả lời")
    st.write(answer)

    if sources:
        st.markdown("### Nguồn tham khảo")
        for i, doc in enumerate(sources, 1):
            src = doc.metadata.get("source", "không rõ")
            with st.expander(f"📄 Nguồn {i}: {src}"):
                st.text(doc.page_content[:400] + "...")
