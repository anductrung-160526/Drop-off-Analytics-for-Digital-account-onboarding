"""
rag_chain.py
------------
Bước "Generation" của RAG: tải FAISS index đã tạo, ghép với LLM
qua một prompt ràng buộc để mô hình CHỈ trả lời dựa trên tài liệu
(giảm hiện tượng bịa thông tin - hallucination).

Module này được dùng lại bởi app.py (giao diện) và có thể test riêng.
"""

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

import config

# Prompt ép mô hình bám sát ngữ cảnh. Nếu không có thông tin -> nói rõ "không tìm thấy".
PROMPT_TEMPLATE = PromptTemplate(
    template=(
        "Bạn là trợ lý hỗ trợ khách hàng của một ngân hàng.\n"
        "Chỉ trả lời dựa trên phần 'Ngữ cảnh' dưới đây. "
        "Tuyệt đối không bịa thông tin.\n"
        "Nếu ngữ cảnh không chứa câu trả lời, hãy nói chính xác: "
        "'Tôi không tìm thấy thông tin này trong tài liệu.'\n\n"
        "Ngữ cảnh:\n{context}\n\n"
        "Câu hỏi: {question}\n\n"
        "Trả lời (ngắn gọn, bằng tiếng Việt):"
    ),
    input_variables=["context", "question"],
)


def load_vectorstore():
    """Tải FAISS index đã lưu từ ingest.py."""
    embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
    return FAISS.load_local(
        config.INDEX_DIR,
        embeddings,
        # Cần cờ này vì FAISS dùng pickle. An toàn vì index do chính ta tạo.
        allow_dangerous_deserialization=True,
    )


def build_qa_chain():
    """Tạo chuỗi hỏi-đáp RAG hoàn chỉnh."""
    config.check_api_key()
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})

    llm = ChatOpenAI(model=config.LLM_MODEL, temperature=config.TEMPERATURE)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,  # Trả về cả nguồn để hiển thị trích dẫn
        chain_type_kwargs={"prompt": PROMPT_TEMPLATE},
    )
    return qa_chain


def ask(qa_chain, question: str):
    """Hỏi một câu, trả về (câu trả lời, danh sách nguồn)."""
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    sources = result.get("source_documents", [])
    return answer, sources


# Cho phép test nhanh trong terminal: python rag_chain.py
if __name__ == "__main__":
    chain = build_qa_chain()
    print("Trợ lý đã sẵn sàng. Gõ 'exit' để thoát.\n")
    while True:
        q = input("Bạn hỏi: ").strip()
        if q.lower() in {"exit", "quit", ""}:
            break
        ans, srcs = ask(chain, q)
        print(f"\nTrả lời: {ans}")
        print("Nguồn: " + ", ".join(
            s.metadata.get("source", "?") for s in srcs
        ) + "\n")
