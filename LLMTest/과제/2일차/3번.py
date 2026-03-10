import streamlit as st
from image_utils import make_image

st.title("프롬프트")

with st.form("img_form"):
    prompt = st.text_input("프롬프트")
    submit = st.form_submit_button("확인")

st.write("생성된 이미지")

if submit:
    if not prompt.strip():
        st.warning("프롬프트를 입력하세요.")
    else:
        with st.spinner("이미지 생성 중..."):
            path = make_image(prompt, "genimage.jpg")
        st.image(path)
