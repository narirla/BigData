import streamlit as st
from module import predict, format_result

st.set_page_config(page_title="이미지 분류(HF)", layout="centered")
st.title("이미지 분류기 (Hugging Face)")

st.caption("이미지를 붙여넣거나 업로드하면 Hugging Face 모델로 분류합니다.")

# 1) 업로드 (붙여넣기/드래그&드롭/파일선택)
uploaded_file = st.file_uploader(
    "이미지 업로드",
    type=["png", "jpg", "jpeg", "webp"]
)

# 2) 옵션 (top_k)
top_k = st.selectbox("상위 결과 개수(top_k)", [1, 3, 5], index=1)

# 3) 메인 처리
if uploaded_file:
    # 이미지 미리보기
    st.image(uploaded_file, caption="입력 이미지", use_container_width=True)

    # 실행 버튼
    if st.button("분류 실행", type="primary"):
        with st.spinner("분류 중... (첫 실행은 모델 다운로드/로딩으로 느릴 수 있음)"):
            # module.py의 predict() 사용 (수업 방식)
            result = predict(uploaded_file, top_k=top_k)

            # 보기 좋게 문자열로 변환 (수업 방식)
            text = format_result(result)

        st.subheader("분류 결과")
        st.text(text)

        # 원본 결과도 확인하고 싶으면(딕셔너리 리스트)
        with st.expander("원본 결과 보기(리스트 형태)"):
            st.write(result)

else:
    st.info("이미지를 업로드하세요. (가능한 환경에서는 Ctrl+V 붙여넣기도 업로드로 동작합니다.)")
