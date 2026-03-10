import streamlit as st
from Lc import chat, format_history, stream_answer

st.title('질문')

if "history" not in st.session_state:
    st.session_state["history"] = []

chain = chat()

with st.form("chat_form"):
    question = st.text_input("질문", key="q", label_visibility="collapsed", placeholder="질문을 입력하세요")
    submit = st.form_submit_button("확인")  
if submit:
    if question.strip() == "":
        st.warning("질문을 입력하세요")
    else:
        answer = st.write_stream(stream_answer(chain, st.session_state["history"], question))

        st.session_state["history"].append({"q": question, "a": answer})

