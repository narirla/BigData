# core/chat/llm.py
# 모델 생성기
from langchain_openai import ChatOpenAI

# gpt = ChatOpenAI(model='gpt-4o', temperature=0)

def get_llm(model: str='gpt-4o', temperature: float=0) :
    return ChatOpenAI(model=model, temperature=temperature)