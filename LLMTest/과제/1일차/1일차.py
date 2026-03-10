# 과제
# 질문: 인공지능에 대해 알려줄래
# 답변:(음성으로 답변)
# 계속하시겠습니까(y/n)?
# 질문: 좀더 간단히 알려줄래
# 답변:음성으로 답변
# 계속하시겠습니까(y/n)?

import os
import openai 
from openai import OpenAI
from IPython.display import Audio, display
import pygame
import time
apiKey = os.getenv('OPENAI_API_KEY')
openai.api_key = apiKey

client = OpenAI()

# 대화 기록 저장용 리스트
conv_history = [{'role':'system', 'content':'You are a helpful teacher'}]

# 누적된 대화 기록(conv_history)응 기반으로 답변 생성
def transcribe_text(conv_history):
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=conv_history)
    return completion.choices[0].message.content

# 텍스트를 음성으로 변환 후 파일에 저장
def text_to_speech(answer_text, out_path):
    tts = client.audio.speech.create(model="tts-1", voice="shimmer", input=answer_text)
    with open(out_path, "wb") as f:
        f.write(tts.read())

# 생성된 mp3 파일 재생
def play_audio(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()

# 반복문
while True:
    question = input("질문: ").strip()
    # print("질문:", question)

    # 질문을 대화 기록에 누적
    conv_history.append({"role": "user", "content": question})

    # 누적된 conv_history로 답변 생성
    answer = transcribe_text(conv_history)

    # 답변도 대화 기록에 누적
    conv_history.append({"role": "assistant", "content": answer})

    print("답변:", answer)  

    # mp3 생성 (덮어쓰기 방지)
    out_path = f"out_{int(time.time())}.mp3"
    text_to_speech(answer, out_path)

    # 음성으로 답변 출력
    play_audio(out_path)
    cont = input("계속하시겠습니까(y/n)? ").strip().lower()
    if cont != "y":
        print("종료합니다.")
        break
