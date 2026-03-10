import os
import openai
import streamlit as st
from openai import OpenAI


if 'client' not in st.session_state:
    apikey = os.getenv('OPENAi_API_KEY')
    openai.api_key=apikey # 키등록
    st.session_state['client'] = OpenAI()

client = st.session_state['client'] # 문제점: 객체가 계속 생성됨 

with st.form('myform'):
    prompt = st.text_input('프롬프트')
    submit = st.form_submit_button('확인')
    if submit:
        s = f'프롬프트:{prompt}'
        with st.spinner('잠시 기다려 주세요....'):
            completion = client.chat.completions.create(model='gpt-3.5-turbo', 
                messages=[{'role':'user','content':prompt}])
        st.write(completion.choices[0].message.content)
