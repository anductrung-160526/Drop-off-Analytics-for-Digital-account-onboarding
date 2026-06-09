"""
agent.py
--------
Phiên bản nâng cao (tùy chọn) gắn từ khóa "Agentic AI".

Agent có thể tự chọn:
- Câu hỏi về định nghĩa/quy định  -> dùng công cụ tra tài liệu (RAG).
- Câu hỏi cần tính toán cụ thể    -> gọi hàm tính phí / tính lãi.

Chạy thử: python agent.py
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool

import config
from rag_chain import build_qa_chain, ask
from tools import ALL_TOOLS


def make_rag_tool():
    """Đóng gói RAG thành một công cụ để agent có thể gọi khi cần tra tài liệu."""
    qa_chain = build_qa_chain()

    def _run(query: str) -> str:
        answer, _ = ask(qa_chain, query)
        return answer

    return Tool(
        name="tra_cuu_tai_lieu_san_pham",
        func=_run,
        description=(
            "Dùng để trả lời câu hỏi về sản phẩm, điều khoản, biểu phí, lãi suất "
            "dựa trên tài liệu ngân hàng. Đầu vào là câu hỏi của khách bằng tiếng Việt."
        ),
    )


def build_agent():
    config.check_api_key()

    tools = [make_rag_tool()] + ALL_TOOLS

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Bạn là trợ lý ngân hàng. Nếu câu hỏi cần tính toán số tiền cụ thể, "
         "hãy gọi công cụ tính. Nếu câu hỏi về quy định/sản phẩm, hãy tra tài liệu. "
         "Trả lời ngắn gọn bằng tiếng Việt."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    llm = ChatOpenAI(model=config.LLM_MODEL, temperature=config.TEMPERATURE)
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


if __name__ == "__main__":
    executor = build_agent()
    print("Agent đã sẵn sàng. Gõ 'exit' để thoát.\n")
    while True:
        q = input("Bạn hỏi: ").strip()
        if q.lower() in {"exit", "quit", ""}:
            break
        result = executor.invoke({"input": q})
        print(f"\nTrả lời: {result['output']}\n")
