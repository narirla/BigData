import os
import streamlit as st
from openai import OpenAI
from time_utils import get_time, getGptResponse


st.markdown("<h1 style='text-align: center;'>세계 시간</h1>", unsafe_allow_html=True)

with st.form('time_form'):
    user_prompt = st.text_input("입력", placeholder="예: 파리의 지금 시간은? / 뉴욕 시간 알려줘")
    submit = st.form_submit_button("확인")

    if submit:
        with st.spinner("GPT가 해당 도시의 시간대 정보를 찾는 중..."):
            response = getGptResponse( user_prompt)
        
        st.write(response )