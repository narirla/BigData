def obesity(height, weight):
    std_weight = (height - 100)*0.85
    obesity_rate = (weight/std_weight)*100

    if obesity_rate < 90:
        result = '저체중'
    elif obesity_rate < 110:
        result = '정상'
    elif obesity_rate < 120:
        result = '과체중'
    else:
        result = '비만'
    
    return std_weight, obesity_rate, result

obesity_img = {
    '저체중': 'under.png',
    '정상': 'normal.png',
    '과체중': 'over.png',
    '비만': 'obese.png',
}

def gen_diet(client, prompt: str):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        text = res.choices[0].message.content.strip()

        lines = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(("-", "•")):
                lines.append(line.lstrip("-• ").strip())

        return lines  # ✅ 그냥 lines만 반환

    except Exception:
        return ["추천 식단을 생성할 수 없습니다."]
