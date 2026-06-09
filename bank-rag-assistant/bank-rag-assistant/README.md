# 🏦 Trợ lý hỏi đáp tài liệu sản phẩm ngân hàng (RAG + Agentic AI)

Trợ lý ảo trả lời câu hỏi của khách hàng về sản phẩm, biểu phí, lãi suất...
dựa trên bộ tài liệu nội bộ của ngân hàng, **có trích dẫn nguồn** để hạn chế
hiện tượng mô hình bịa thông tin (hallucination).

Dự án minh hoạ kỹ thuật **RAG (Retrieval-Augmented Generation)** và bước đầu
tiếp cận **Agentic AI** — mô hình tự chọn công cụ phù hợp (tra tài liệu hoặc
tính toán) cho từng câu hỏi.

## 🎯 Bài toán

Khách hàng thường hỏi đi hỏi lại các thông tin có sẵn trong tài liệu (lãi suất,
phí, điều kiện sản phẩm). Thay vì để LLM trả lời tự do (dễ sai), hệ thống truy
hồi đúng đoạn tài liệu liên quan rồi mới sinh câu trả lời, kèm nguồn để kiểm chứng.

## 🏗️ Kiến trúc

```
Tài liệu (PDF/TXT/MD)
        │  ingest.py
        ▼
   Cắt nhỏ (chunk)  ──►  Embedding  ──►  FAISS Vector Store
                                              │
Câu hỏi ──►  Truy hồi top-k chunk liên quan ──┘
        │
        ▼
   LLM + Prompt ràng buộc  ──►  Câu trả lời + Nguồn trích dẫn
```

Phiên bản agent (`agent.py`) bổ sung khả năng tự gọi công cụ tính phí / tính lãi.

## 📁 Cấu trúc thư mục

```
bank-rag-assistant/
├── data/                  # Tài liệu nguồn (mẫu sẵn có)
├── config.py              # Cấu hình tập trung
├── ingest.py              # Nạp dữ liệu -> FAISS index
├── rag_chain.py           # Logic RAG dùng chung
├── tools.py               # Công cụ cho agent (tính phí, tính lãi)
├── agent.py               # Phiên bản Agentic AI (tùy chọn)
├── app.py                 # Giao diện web (Streamlit)
├── requirements.txt
├── .env.example           # Mẫu file cấu hình API key
└── .gitignore
```

## 🚀 Cách chạy

### 1. Cài đặt môi trường

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Thiết lập API key

Sao chép `.env.example` thành `.env` rồi điền key của bạn:

```bash
cp .env.example .env
# Mở .env và thay bằng OPENAI_API_KEY thật
```

### 3. Nạp dữ liệu vào vector store

```bash
python ingest.py
```

### 4. Chạy ứng dụng

```bash
streamlit run app.py
```

Mở trình duyệt tại địa chỉ Streamlit hiển thị (thường là http://localhost:8501).

### 5. (Tùy chọn) Thử phiên bản agent trong terminal

```bash
python agent.py
```

## 🧠 Một số điểm kỹ thuật đáng chú ý

- **Chunking:** `chunk_size=500`, `overlap=50`. Chunk quá lớn gây nhiễu khi truy
  hồi; quá nhỏ làm mất ngữ cảnh; phần gối đầu (overlap) tránh cắt ngang ý.
- **Chống hallucination:** prompt ràng buộc mô hình chỉ trả lời theo ngữ cảnh,
  trả về "không tìm thấy" nếu tài liệu không có thông tin.
- **Trích dẫn nguồn:** mỗi câu trả lời kèm đoạn tài liệu gốc để người dùng kiểm chứng.
- **Agentic:** agent tự quyết định dùng RAG hay gọi hàm tính toán theo loại câu hỏi.

## ⚠️ Lưu ý

- Dữ liệu trong `data/` là **mẫu giả lập**, không phải số liệu thật của bất kỳ
  ngân hàng nào.
- Không commit file `.env` (chứa API key) lên GitHub — đã được loại trong `.gitignore`.

## 🔧 Hướng phát triển tiếp

- Thêm bộ nhớ hội thoại (lịch sử chat) để hỏi nối tiếp.
- Đánh giá chất lượng truy hồi (retrieval) bằng tập câu hỏi/đáp án mẫu.
- Thử các mô hình embedding/LLM khác nhau và so sánh.
