import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'

df = pd.read_csv('data/grade.csv', index_col='이름')

st.title('학생점수 현황')
st.markdown('---')
# st.dataframe( df, use_container_width=True ) version up: use_container_width -> width
st.dataframe( df, width='stretch' )

st.markdown('## 바차트')
ax = df.plot( kind='bar', rot=45, ylabel='점수', ylim=(0,100), title="성적현황", grid=True )
# ax = df.plot( kind='bar', y=['국어','영어'],
#              rot=45, ylabel='점수', ylim=(0,100), title="성적현황",grid=True )

# ax = df.plot( kind='pie', y='국어',autopct="%.2f" , legend=False)
# ax = df.plot( kind='scatter', y='국어',x='수학', s=100, c='r')
# ax = df.plot( kind='hist', y='국어', bins=[0,10,20,30,40,50,60,70,80,90]) #range(0,101,10)
st.pyplot( ax.figure ) # 웹에 창을 띄움