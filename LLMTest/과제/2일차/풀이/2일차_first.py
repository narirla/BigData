import streamlit as st
from gptchat import prompt, bmi, prompt_stream

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

        with st.spinner("답변기다리는중"):
            # text = prompt(result + "추천 식단")
            stream = prompt_stream(result + "추천 식단")
        # st.text(text)
        st.write_stream( stream)
