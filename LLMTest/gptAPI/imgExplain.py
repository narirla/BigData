from openai import OpenAI
import base64

client = OpenAI()

# 로컬 이미지를 인코딩 이미지로 변경해주는 함수
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    
# api를 이용해서 이미지를 설명하는 함수
def img_explain(file_path):
    image_base64 = encode_image(file_path)  # file_path를 인자로 받아옴

    data_url = f"data:image/jpeg;base64,{image_base64}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "이 이미지에 대해 설명해줘"},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }]
    )
    return response.choices[0].message.content