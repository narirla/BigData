# 1. Python 이미지를 기반으로 설정 (Python 3.10 사용)
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 현재 디렉토리의 파일을 컨테이너의 /app 디렉토리로 복사
COPY app.py .

# 4. 파이썬 스크립트 실행
CMD ["python", "app.py"]