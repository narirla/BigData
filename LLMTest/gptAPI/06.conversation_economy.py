from openai import OpenAI
import openai
import os

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
client = OpenAI()  

conversation_history = [
    {'role': 'system', 'content': 'You are a helpful assistant.'}
]

SUMMARY_TRIGGER_LENGTH = 10

def chat_with_gpt(user_input):
    conversation_history.append({'role': 'user', 'content': user_input})

    if len(conversation_history) > SUMMARY_TRIGGER_LENGTH:
        summarize_and_reset_history()

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=conversation_history
    )
    assistant_reply = response.choices[0].message.content
    conversation_history.append({'role': 'assistant', 'content': assistant_reply})

    return assistant_reply

def summarize_and_reset_history():
    # 요약 요청 메시지 추가
    summary_request = conversation_history + [{'role': 'user', 'content': '지금까지의 대화를 간단히 요약해줘.'}]
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=summary_request
    )
    summary = response.choices[0].message.content

    # 대화 기록 리셋 후 요약 포함
    conversation_history.clear()
    conversation_history.append({'role': 'system', 'content': 'You are a helpful assistant.'})
    conversation_history.append({'role': 'user', 'content': '이전 대화 요약: ' + summary})

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    assistant_reply = chat_with_gpt(user_input)
    print(f"GPT: {assistant_reply}")
