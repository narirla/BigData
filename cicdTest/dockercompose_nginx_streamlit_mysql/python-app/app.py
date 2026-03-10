import streamlit as st
import pymysql
import os
import pandas as pd
import time

# 페이지 제목 설정
st.set_page_config(page_title="DB Data Viewer")
st.title("📊 MySQL 데이터 목록 (Streamlit)")

# 탭 사이즈 키우기(CSS)
st.markdown(
    """
    <style>
    /* 탭 영역 */
    div[data-baseweb="tab-list"]{
        gap: 24px !important;
        padding-bottom: 6px !important;
    }

    /* 탭 버튼(입력/보기) */
    div[data-baseweb="tab-list"] button[role="tab"]{
        font-size: 26px !important;      /* 글자 크게 */
        padding: 18px 34px !important;   /* 클릭 영역 크게 */
        min-height: 64px !important;     /* 높이 */
        border-radius: 10px !important;  /* 모서리 */
    }

    /* 선택된 탭 강조 */
    div[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"]{
        font-weight: 800 !important;
        border-bottom: 4px solid #ff4b4b !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# [변경] 입력 성공 메시지 유지용 상태값
if "insert_success" not in st.session_state:
    st.session_state.insert_success = False

# DB 연결 함수
def get_db_connection(retry=30, wait=2):
    for _ in range(retry):
        try:
            return pymysql.connect(
                host=os.environ.get('DB_HOST', 'mysql'),
                user=os.environ.get('DB_USER', 'scott'),
                password=os.environ.get('DB_PASS', 'tiger'),
                database=os.environ.get('DB_NAME', 'mydb'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception:
            time.sleep(wait)
    raise RuntimeError("MySQL 연결 실패(타이밍/상태 확인 필요)")

tab_input, tab_view = st.tabs(["입력", "보기"])


with tab_input:
    st.subheader("제품 입력")

    if st.session_state.insert_success:
        st.success("제품이 성공적으로 등록되었습니다.")
        st.session_state.insert_success = False

    with st.form("input_form"):
        pname = st.text_input("제품명")
        quantity = st.number_input("수량", min_value=1, step=1)
        mfg_date = st.date_input("생산일")
        submit_button = st.form_submit_button("입력")

    if submit_button:
        if not pname.strip():
            st.error("제품명을 입력하세요.")
        else:
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO product (pname, quantity, mfg_date)
                        VALUES (%s, %s, %s)
                        """,
                        (pname.strip(), int(quantity), mfg_date)
                    )
                conn.commit()

                # [변경] 성공 메시지 유지 플래그 세팅 후 rerun
                st.session_state.insert_success = True
                st.rerun()

            except Exception as e:
                msg = str(e)
                # [추가] PK 중복 입력 시 사용자 친화 메시지
                if "Duplicate entry" in msg:
                    st.error("이미 존재하는 제품명입니다. 다른 제품명을 입력하세요.")
                else:
                    st.error(f"데이터베이스 오류: {e}")

            finally:
                if 'conn' in locals():
                    conn.close()


with tab_view:
    st.subheader("제품 목록(보기)")

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT pname AS '제품명',
                quantity AS '수량',
                mfg_date AS '생산일'
                FROM product
                ORDER BY mfg_date DESC, pname ASC
            """)
            rows = cursor.fetchall()

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.success(f"총 {len(rows)}개의 데이터를 불러왔습니다.")
        else:
            st.info("조회된 데이터가 없습니다.")

    except Exception as e:
        st.error(f"조회 실패: {e}")

    finally:
        if 'conn' in locals():
            conn.close()
