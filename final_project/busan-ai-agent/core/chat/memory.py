# core/chat/memory.py
# summary
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 서머리 제한 상수
SUMMARY_TRIGGER_LENGTH = 10

BASE_SYSTEM = "너는 부산 청년을 돕는 AI 에이전트다."

def maybe_summarize(conversation_history, llm, trigger_len: int = SUMMARY_TRIGGER_LENGTH):
    if len(conversation_history) <= trigger_len:
        return conversation_history

    summary_request = conversation_history + [
        HumanMessage(content="지금까지의 대화를 간단히 요약해줘")
    ]
    response = llm.invoke(summary_request)
    summary = response.content

    conversation_history.clear()
    conversation_history.append(SystemMessage(content=BASE_SYSTEM))
    conversation_history.append(AIMessage(content=f"[대화 요약]\n{summary}"))
    # print(f"[요약완료] {summary}")
    # system_prompt = f"""
    #     You are a helpful assistant.
    #     Here is the summary of the previous conversation: {summary}
    #     Please continue the conversation based on this summary.
    #     """.strip()
    # conversation_history.append(SystemMessage(content=system_prompt))
    print(f"[요약완료] {summary}")
    return conversation_history

