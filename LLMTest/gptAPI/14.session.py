import streamlit as st

print('call') # Streamlit 앱이 실행(초기 로딩)될 때 콘솔에 출력됨
# st.session_state "세션(사용자 접속)" 동안 값을 유지하는 저장 공간
if 'my' not in st.session_state:
    st.session_state['my']=[]
# my = []
with st.form('myform'):
    prompt = st.text_input('프롬프트 : ')
    submit = st.form_submit_button('요청')
    if submit:
        # my.append(prompt)
        st.session_state['my'].append(prompt)
        print('my:', st.session_state['my'])
        st.write( prompt )

