# ui/components/chat_ui.py
# 채팅 랜더링, 입력 폼
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def render_history(conversation_history, height=500):
    if len(conversation_history) > 1:
        chat_container = st.container(height=height, border=True)
    else :
        chat_container = st.container(border=False)

    with chat_container:
        for message in conversation_history:
            if isinstance(message, SystemMessage):
                continue
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
    return chat_container