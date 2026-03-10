import streamlit as st
import pymysql
import os
import pandas as pd

# 페이지 제목 설정
st.set_page_config(page_title="DB Data Viewer")
st.title("📊 MySQL 데이터 목록 (Streamlit)")

# DB 연결 함수
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'mysql'),
        user=os.environ.get('DB_USER', 'scott'),
        password=os.environ.get('DB_PASS', 'tiger'),
        database=os.environ.get('DB_NAME', 'mydb'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    conn = get_db_connection()
    # query = "SELECT * FROM users"
    # df = pd.read_sql_query(query, conn)
    # st.header("데이터 테이블")
    # df.dataframe(df, use_container_width=True)

    with conn.cursor() as cursor:
        # 'users' 테이블 데이터를 가져옴 (실제 테이블명으로 수정하세요)
        # rows = [{'id': 1, 'username': 'user1', 'email': 'user1@example.com'}, 
        #         {'id': 2, 'username': 'user2', 'email': 'user2@example.com'}]
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
    
    if rows:
        # Pandas DataFrame을 사용하여 깔끔한 표로 출력
        df = pd.DataFrame(rows)
        st.subheader("데이터 테이블")
        st.dataframe(df, use_container_width=True) 
        
        # 간단한 통계나 차트도 추가 가능
        st.success(f"총 {len(rows)}개의 데이터를 불러왔습니다.")
    else:
        st.info("조회된 데이터가 없습니다.")

except Exception as e:
    st.error(f"DB 연결 실패: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
