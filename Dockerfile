# Dockerfile.server
# server(=zero-to-agile-ai-server) 기반으로 FastAPI 서버 이미지 생성

FROM python:3.12-slim

WORKDIR /srv

# unzip 설치 (zip을 풀기 위함)
RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

# 1) server 복사
COPY zero-to-agile-ai-server ./zero-to-agile-ai-server

# 2) 압축 해제
RUN unzip /srv/zero-to-agile-ai-server -d /srv \
    && rm /srv/zero-to-agile-ai-server

# zip 안쪽 폴더로 이동
WORKDIR /srv/zero-to-agile-ai-server

# 3) 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 4) 런타임 환경변수(포트 등)는 docker-compose에서 주입
EXPOSE 8000

# 5) FastAPI 실행 (app/main.py 안의 app 객체)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
