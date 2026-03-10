import os
import requests
from openai import OpenAI

def make_image(prompt: str, out_path: str = "genimage.jpg") -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    res = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    image_url = res.data[0].url
    image_data = requests.get(image_url).content

    with open(out_path, "wb") as f:
        f.write(image_data)

    return out_path
