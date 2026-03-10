FROM python:3.9-slim

# 필요한 패키지 설치
RUN pip install streamlit pymysql pandas

WORKDIR /app
COPY . .

# Streamlit 기본 포트는 8501입니다.
EXPOSE 8501

# Streamlit 실행 명령어
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
