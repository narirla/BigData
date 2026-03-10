import os
import openai
from openai import OpenAI
apiKey = os.getenv('OPENAI_API_KEY')
openai.api_key = apiKey 

client = OpenAI()

def prompt(prompt_text):
    completion = client.chat.completions.create(model='gpt-4o',
                                    messages=[{'role':'user', 'content':prompt_text}] )

    return completion.choices[0].message.content

def prompt_stream(prompt_text):
    stream = client.chat.completions.create(model='gpt-4o',
                messages=[{'role':'user', 'content':prompt_text}],stream=True )
    return stream


def bmi(height, weight):
    standard_weight = (float(height) - 100) * 0.85
    bmi = float(weight) / float(standard_weight) * 100
    if bmi < 90:
        return "저체중", "under"
    elif 90 <= bmi < 110:
        return "정상", "normal"
    elif 110 <= bmi < 120:
        return "과체중", "over"
    else:
        return "비만", "obese"
