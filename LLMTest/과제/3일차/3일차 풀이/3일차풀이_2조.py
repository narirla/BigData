import streamlit as st

from langchain_core.messages import AIMessage, SystemMessage
from fc import chat

st.set_page_config(page_title="랭체인 실시간 답변")
st.title("랭체인 실시간 답변")

if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = [SystemMessage(content='You are a helpful assistant')]

chat_history = st.session_state['chat_history']

with st.form('myform'):
    prompt = st.text_input('질문 :')
    submit = st.form_submit_button('확인')

    if submit and prompt:
        response = chat(prompt, chat_history)
        rst = st.write_stream( response )
        chat_history.append( AIMessage(content=rst) )
