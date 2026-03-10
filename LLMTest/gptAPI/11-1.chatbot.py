import streamlit as st
from gptchat import prompt

with st.form('myform'):
    prompt_text = st.text_input('프롬프트: ') 
    submit = st.form_submit_button('확인')
    if submit:
        s = f'프롬프트: {prompt_text}'
        with st.spinner('잠시 기다려 주세요...'):
            rst = prompt(prompt_text)
        st.write( rst )

