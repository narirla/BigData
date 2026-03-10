import streamlit as st
from timefn import getGptResponse
   
st.markdown("<h1 style='text-align: center;'>세계 시간</h1>", unsafe_allow_html=True)

with st.form('time_form'):
    user_prompt = st.text_input("입력", placeholder="예: 파리의 지금 시간은? / 뉴욕 시간 알려줘")
    submit = st.form_submit_button("확인")

    if submit:
        with st.spinner("GPT가 해당 도시의 시간대 정보를 찾는 중..."):
            response = getGptResponse( user_prompt)
        
        st.write(response )




# import streamlit as st
# import os
# import json
# from datetime import datetime
# import pytz 
# import openai
# from openai import OpenAI

# if 'client' not in st.session_state:
#     apiKey = os.getenv('OPENAI_API_KEY')
#     openai.api_key = apiKey
#     st.session_state['client'] = OpenAI()

# client = st.session_state['client']


# def get_time(timezone_str):
#     try:
#         tz = pytz.timezone(timezone_str)
#         now = datetime.now(tz)
#         # city_name = timezone_str.split('/')[-1].replace('_', ' ')
#         return now.strftime(f"%Y년 %m월 %d일 %H시 %M분 %S초")
#     except Exception as e:
#         return f"시간을 알 수 없습니다: {timezone_str}"

# time_tool = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_time",
#             "description": "특정 도시의 현재 시간을 알려줍니다.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "timezone_str": {
#                         "type": "string",
#                         "description": "구하려는 도시의 IANA Timezone 문자열 (예: Asia/Seoul)",
#                     },
#                 },
#                 "required": ["timezone_str"],
#             },
#         }
#     }
# ]
    
# st.markdown("<h1 style='text-align: center;'>세계 시간</h1>", unsafe_allow_html=True)

# with st.form('time_form'):
#     user_prompt = st.text_input("입력", placeholder="예: 파리의 지금 시간은? / 뉴욕 시간 알려줘")
#     submit = st.form_submit_button("확인")

#     if submit:
#         messages = [{"role": "user", "content": user_prompt}]
        
#         with st.spinner("GPT가 해당 도시의 시간대 정보를 찾는 중..."):
#             try:
#                 response = client.chat.completions.create(
#                     model="gpt-3.5-turbo",
#                     messages=messages,
#                     tools=time_tool,
#                     tool_choice="auto" 
#                 )
#                 response_message = response.choices[0].message
#                 tool_calls = response_message.tool_calls

#                 args = json.loads(tool_calls[0].function.arguments)
#                 tz_str = args.get('timezone_str')
                
#                 function_result = get_time(tz_str)
#                 messages.append( {'role':'function','name':'get_time','content':json.dumps(function_result)} )
#                 response =client.chat.completions.create( model='gpt-4o',messages= messages )
#                 st.success(response.choices[0].message.content)
                    
#             except Exception as e:
#                 print( response.choices[0].message.content)
#                 # st.error(f"오류 발생: {e}")