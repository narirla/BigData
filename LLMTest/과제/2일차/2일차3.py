import streamlit as st
from openai import OpenAI
import openai
import os

if "client" not in st.session_state:
    api_key = os.getenv('OPENAI_API_KEY')
    openai.api_key = api_key
    st.session_state['client']  = OpenAI()

def GPT(prompt):
    completion = st.session_state['client'].images.generate(
        model='dall-e-3', size="1024x1024", quality="standard",n=1,prompt=prompt)
    return completion.data[0].url

st.title( '프롬프트')
st.markdown('---')

# 안에 영역 생성
with st.form('myform'): 
    prompt = st.text_input('프롬프트', placeholder="입력")
    submit = st.form_submit_button('확인')
    if submit:
        with st.spinner('이미지를 그리는 중...'):
            image_url = GPT(prompt)
            if image_url:
                st.image(image_url, use_container_width=True)