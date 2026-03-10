import os
import json
from datetime import datetime
import pytz 
import openai
from openai import OpenAI


apiKey = os.getenv('OPENAI_API_KEY')
openai.api_key = apiKey
client = OpenAI()


time_tool = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "특정 도시의 현재 시간을 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone_str": {
                        "type": "string",
                        "description": "구하려는 도시의 IANA Timezone 문자열 (예: Asia/Seoul)",
                    },
                },
                "required": ["timezone_str"],
            },
        }
    }
]


def get_time(timezone_str):
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        return now.strftime(f"%Y년 %m월 %d일 %H시 %M분 %S초")
    except Exception as e:
        return f"시간을 알 수 없습니다: {timezone_str}"


def getGptResponse( user_prompt):
    messages = [{"role": "user", "content": user_prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=time_tool,
            tool_choice="auto" 
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        args = json.loads(tool_calls[0].function.arguments)
        tz_str = args.get('timezone_str')
        function_result = get_time(tz_str)
        print(function_result)
        messages.append( {'role':'function','name':'get_time','content':json.dumps(function_result)} )
        response =client.chat.completions.create( model='gpt-4o-mini',messages= messages )
        return response.choices[0].message.content
            
    except Exception as e:
        return response.choices[0].message.content
