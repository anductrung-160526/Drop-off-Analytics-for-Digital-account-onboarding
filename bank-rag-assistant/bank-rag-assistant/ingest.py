"""
ingest.py
---------
Bước "Retrieval" của RAG: đọc tài liệu trong thư mục data/,
cắt nhỏ thành chunk, tạo embedding và lưu vào FAISS index.

Chạy MỘT LẦN (và chạy lại mỗi khi thay đổi dữ liệu):
    python ingest.py
"""

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

import config


def load_documents():
    """Đọc tất cả file PDF, TXT, MD trong thư mục data/."""
    loaders = [
        DirectoryLoader(config.DATA_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(config.DATA_DIR, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(config.DATA_DIR, glob="**/*.md", loader_cls=TextLoader),
    ]

    docs = []
    for loader in loaders:
        try:
            docs.extend(loader.load())
        except Exception as e:
            print(f"  (Bỏ qua một loader do lỗi: {e})")

    if not docs:
        raise FileNotFoundError(
            f"Không tìm thấy tài liệu nào trong '{config.DATA_DIR}/'. "
            "Hãy thêm file .pdf / .txt / .md vào đó."
        )

    print(f"Đã nạp {len(docs)} tài liệu nguồn.")
    return docs


def split_documents(docs):
    """Cắt tài liệu thành các chunk nhỏ có gối đầu."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Đã tạo {len(chunks)} chunk (size={config.CHUNK_SIZE}, "
          f"overlap={config.CHUNK_OVERLAP}).")
    return chunks


def build_index(chunks):
    """Tạo embedding cho từng chunk và lưu vào FAISS."""
    embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(config.INDEX_DIR)
    print(f"Đã lưu vector index vào '{config.INDEX_DIR}/'.")


def main():
    config.check_api_key()
    print("=== Bắt đầu nạp dữ liệu ===")
    docs = load_documents()
    chunks = split_documents(docs)
    build_index(chunks)
    print("=== Hoàn tất! Giờ bạn có thể chạy: streamlit run app.py ===")


if __name__ == "__main__":
    main()
