import os
import streamlit as st
from openai import OpenAI
from obesity_utils import obesity, gen_diet

client = OpenAI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 2번.py 위치

obesity_img = {
    "저체중": os.path.join(BASE_DIR, "비만도", "under.png"),
    "정상": os.path.join(BASE_DIR, "비만도", "normal.png"),
    "과체중": os.path.join(BASE_DIR, "비만도", "over.png"),
    "비만": os.path.join(BASE_DIR, "비만도", "obese.png"),
}

with st.form('myform'):
    st.header('비만도')

    height = st.number_input('키(cm) : ')
    weight = st.number_input('몸무게(kg) : ')
    sumbit = st.form_submit_button('결과')

    if sumbit:
        std_w, rate, result = obesity(height, weight)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"표준체중: {std_w:.2f} kg")
            st.write(f"비만도: {rate:.2f}")
            st.write(f"판정: {result}")
        with col2:
            # 결과별 이미지 출력
            img_path = obesity_img.get(result)

            if img_path:
                st.image(img_path, caption=result, width=250)
            else:
                st.warning("해당 결과에 대한 이미지가 없습니다.")

        st.write("### 결과별 추천 식단")
        prompt = f"{result}인 사람 추천 식단 3개 bullet로 알려줘"

        diet_lines = gen_diet(client, prompt)

        if diet_lines:
            for line in diet_lines:
                st.write(f"- {line}")
        else:
            st.warning("추천 식단을 생성할 수 없습니다.")

