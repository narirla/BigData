# module.py
from transformers import pipeline
from PIL import Image

# 1) 사용할 모델명(허깅페이스)
# 변경 사항: 다른 모델로 바꾸려면 여기만 수정
MODEL_NAME = "google/vit-base-patch16-224"

# 2) pipeline은 무겁기 때문에 1번만 만들고 재사용(캐시)
pipe = None

def load_model():
    """
    이미지 분류 파이프라인을 1회만 로드해서 재사용
    CPU 사용: device=-1
    """
    global pipe
    if pipe is None:
        pipe = pipeline(
            task="image-classification",
            model=MODEL_NAME,
            device=-1   # CPU 고정
        )
    return pipe


def predict(uploaded_file, top_k=3):
    """
    uploaded_file: Streamlit의 st.file_uploader 결과(UploadedFile)
    top_k: 상위 결과 몇 개 볼지
    return: 결과 리스트(딕셔너리 리스트)
            예) [{'label': 'tabby', 'score': 0.82}, ...]
    """
    img = Image.open(uploaded_file).convert("RGB")
    model = load_model()
    result = model(img, top_k=top_k)
    return result


def format_result(result):
    """
    result(list)를 사람이 읽는 문자열로 변환
    JSON 안 배웠으니 문자열로만 출력용 처리
    """
    lines = []
    for i, r in enumerate(result, start=1):
        label = r["label"]
        score = r["score"]
        lines.append(f"{i}) 라벨: {label} / 신뢰도: {score:.3f}")
    return "\n".join(lines)
