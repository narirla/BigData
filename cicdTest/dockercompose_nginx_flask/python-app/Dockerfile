FROM python:3.9-slim

# MySQL 접속을 위한 라이브러리 설치
RUN pip install flask pymysql

WORKDIR /app
COPY . .

# Flask 실행 (5000번 포트)
CMD ["python", "app.py"]
