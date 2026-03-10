# 1. Python 베이스 이미지
FROM python:3.10-slim

# 2. 작업 디렉토리 (프로젝트 루트)
WORKDIR /app
# 2-1. PYTHONPATH 설정
ENV PYTHONPATH=/app

# 3. 의존성 먼저 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 필요한 소스만 복사
COPY core ./core
COPY ui ./ui

# 5. Streamlit 포트
EXPOSE 8501

# 6. Streamlit 실행
# --server.address=0.0.0.0 설정이 있어야 외부 접속 가능
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
