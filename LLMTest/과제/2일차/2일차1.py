import streamlit as st
import os
import openai
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

client = OpenAI()


def prompt(text):
    with st.spinner("잠시만 기다려 주세요..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content


def bmi(height, weight):
    standard_weight = (float(height) - 100) * 0.85
    bmi = float(weight) / float(standard_weight) * 100
    if bmi < 90:
        return "저체중", "under"
    elif 90 <= bmi < 110:
        return "정상", "normal"
    elif 110 <= bmi < 120:
        return "과체중", "over"
    else:
        return "비만", "obese"


with st.form("bmi_form"):
    st.title("비만도")
    
    height = st.number_input("키 :")
    weight = st.number_input("몸무게 :")
    submit = st.form_submit_button("결과")

    if submit:
        result, image = bmi(height, weight)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"키: {height}")
            st.write(f"몸무게: {weight}")
            st.write(f"결과: {result}")

        with col2:
            image_path = f"image/{image}.png"
            st.image(image_path)

        text = prompt(result + "추천 식단")
        st.text(text)
