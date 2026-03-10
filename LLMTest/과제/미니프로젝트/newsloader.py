from langchain_community.document_loaders import WebBaseLoader

MAX_CHARS = 6000

def clean_newlines(text: str) -> str:
    return ' '.join(text.split())

def load_news_text(url: str, max_chars: int = MAX_CHARS) -> str:
    webloader = WebBaseLoader([url])
    docs = webloader.load()

    cleaned_texts = []
    for doc in docs:
        cleaned_texts.append(clean_newlines(doc.page_content))

    # 본문 후보: 가장 긴 텍스트 1개
    main_text = max(cleaned_texts, key=len)

    return main_text[:max_chars]
