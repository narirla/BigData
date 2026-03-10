import streamlit as st
from PIL import Image
from imgExplain import img_explain

st.title('이미지 업로드')

upfile = st.file_uploader('이미지 업로드',type=['jpg','png','jpeg'] )

if upfile is not None:
    print( 'upfile type', type(upfile) )
    print( upfile.name)
    image = Image.open( upfile)
    st.image(image)

    image.save(f'uploadfile\{upfile.name}')
    with st.spinner('이미지 설명 생성 중...'):
        result = img_explain(f'uploadfile\{upfile.name}')
    st.write(result)
    # st.success(f'서버에 저장됨:{upfile.name}')