import os
import openai 
from openai import OpenAI
apiKey = os.getenv('OPENAI_API_KEY')
openai.api_key = apiKey

client = OpenAI()
def prompt(prompt_text):
    completion = client.chat.completions.create(model='gpt-4o',
                                            messages=[{'role':'user','content': prompt_text}])
    
    return completion.choices[0].message.content
