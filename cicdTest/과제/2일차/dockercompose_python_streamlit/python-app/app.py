import pymysql  # mysql.connector 대신 pymysql 사용
import time
import pandas as pd
import streamlit as st

# -----------------------------------------------
# 1번
# -----------------------------------------------

st.subheader("입력 테스트")
if "input_name" not in st.session_state:
    st.session_state.input_name = ""

with st.form("name_form"):
    name = st.text_input("이름", value="")
    submit_name = st.form_submit_button("입력")

    if submit_name:
        st.session_state.input_name = name

st.write(f"입력된 이름: {st.session_state.input_name}")

st.divider()

# -----------------------------------------------
# 2번
# -----------------------------------------------

st.title("Product table")

# MySQL 연결
def connect_to_mysql():
    while True:
        try:
            return pymysql.connect(
                host="db",  # compose 서비스명
                user="testuser",
                password="testpassword",
                database="testdb",
                charset="utf8mb4"
            )
        except pymysql.MySQLError:
            time.sleep(2)

# product 테이블 데이터를 조회 -> DataFrame으로 반환
def fetch_products():
    conn = connect_to_mysql()
    try:
        df = pd.read_sql("SELECT id, name, price FROM product", conn)
        return df
    finally:
        conn.close()

# 처음 실행할 때만 df를 만들고 이후엔 세션값 재사용
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["id", "name", "price"])

# 데이터프레임 출력
st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

with st.form("product_form", border=False):
    submit_products = st.form_submit_button("보기")

    # "보기" 버튼 클릭 시 DB 조회 후 결과를 세션에 저장
    if submit_products:
        st.session_state.df = fetch_products()
        st.rerun()



