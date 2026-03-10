from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

template = "이전 대화:{history}\n질문:{question}\n답변:"

def format_history(history):
    return "\n\n".join([f"질문: {h['q']}\n답변: {h['a']}" for h in history])

def chat():
    gpt = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = PromptTemplate(
        input_variables=["history", "question"],
        template=template
    )
    return prompt | gpt | StrOutputParser()

def stream_answer(chain, history: list[dict], question: str):
    history_txt = format_history(history)
    for chunk in chain.stream({"history": history_txt, "question": question}):
        yield chunk
