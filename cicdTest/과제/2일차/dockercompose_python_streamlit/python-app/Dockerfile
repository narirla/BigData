# Python 이미지에서 시작
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# 필요한 패키지 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 기본 명령어 설정
CMD ["python", "app.py"]
