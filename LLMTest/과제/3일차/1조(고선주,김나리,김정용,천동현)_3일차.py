import streamlit as st
from langchain_my import chat, format_history

st.title('질문')

if "history" not in st.session_state:
    st.session_state["history"] = []

chain = chat()

with st.form("chat_form"):
    question = st.text_input("질문을 입력하세요")
    submit = st.form_submit_button("확인")

if submit:
    if question.strip() == "":
        st.warning("질문을 입력하세요")
    else:
        history_txt = format_history(st.session_state["history"])

        placeholder = st.empty()
        answer = ""

        for chunk in chain.stream({
            "history": history_txt,
            "question": question
        }):
            answer += chunk
            placeholder.markdown(answer)

        st.session_state["history"].append({"q": question, "a": answer})

st.divider()

for h in st.session_state["history"]:
    st.markdown(f"질문: {h['q']}")
    st.markdown(f"답변: {h['a']}")
    st.markdown("-"*50)
