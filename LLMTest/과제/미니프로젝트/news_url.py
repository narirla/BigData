import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from newsloader import load_news_text

st.set_page_config(page_title="기사 요약", layout="wide")
st.title("기사 요약")

model_name = "gpt-3.5-turbo"

# LLM
llm = ChatOpenAI(model=model_name, temperature=0)

# 0) 단일 요약(짧은 글용)
single_prompt = PromptTemplate.from_template("""
너는 뉴스 요약 전문가다. 아래 기사 본문을 한국어로 요약하라.

[출력]
- 요약(3~5문장)
- 핵심 포인트 5개(번호)
- 키워드 5개(쉼표)

[기사 본문]
{text}
""")
single_chain = single_prompt | llm | StrOutputParser()

# 1) 1차 요약(청크 요약)
chunk_prompt = PromptTemplate.from_template("""
너는 뉴스 요약 전문가다. 아래 기사 일부를 한국어로 간단 요약하라.
- 2~3문장
- 핵심 키워드 3개(쉼표)

[기사 일부]
{text}
""")
chunk_chain = chunk_prompt | llm | StrOutputParser()

# 2) 2차 요약(메타 요약)
meta_prompt = PromptTemplate.from_template("""
너는 뉴스 요약 전문가다.
아래 '부분 요약들'을 종합하여 최종 요약을 한국어로 작성하라.

[출력]
- 요약(3~5문장)
- 핵심 포인트 5개(번호)
- 키워드 5개(쉼표)

[부분 요약들]
{summaries}
""")
meta_chain = meta_prompt | llm | StrOutputParser()

def summarize_text(text: str) -> str:
    # 짧은 글: 단일 요약
    if len(text) <= 6000:
        return single_chain.invoke({"text": text})

    # 긴 글: 분할 → 청크 요약 → 종합 요약
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = splitter.split_text(text)

    partials = []
    for i, ch in enumerate(chunks, start=1):
        s = chunk_chain.invoke({"text": ch})
        partials.append(f"[{i}] {s}")

    joined = "\n".join(partials)
    return meta_chain.invoke({"summaries": joined})

# ===== UI =====
url = st.text_input("기사 url을 입력해주세요.")
run = st.button("요약 생성")

if run:
    if not url.strip():
        st.warning("url을 입력해주세요")
        st.stop()

    with st.spinner("기사를 불러오는 중..."):
        text = load_news_text(url)

    if len(text) < 200:
        st.error("기사 본문을 충분히 가져오지 못했습니다.")
        st.stop()

    with st.spinner("요약을 생성하는 중..."):
        summary = summarize_text(text)

    st.subheader("요약 결과")
    st.markdown(summary)
