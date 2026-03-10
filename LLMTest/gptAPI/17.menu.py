import streamlit as st
from streamlit_option_menu import option_menu
import home
import intro
import setting


with st.sidebar:

    selected = option_menu( 
        menu_title="메뉴제목",
        options=['홈','소개','설정'],
        icons=["house","info-circle",'gear'],
        menu_icon="cast",
        default_index=0  )

if selected =='홈':
    # st.title("여기는 홈입니다.")
    home.home("홍길동")
elif selected == '소개':
    # st.title("여기는 소개입니다.")
    intro.intro()
elif selected == '설정':
    # st.title('여기는 설정입니다.')
    setting.setting()