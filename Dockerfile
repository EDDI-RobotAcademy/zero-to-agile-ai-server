# Dockerfile
# - zip 없이 레포에 있는 zero-to-agile-ai-server/ 소스 폴더를 그대로 복사해서 실행
# - 컨테이너 내부 작업 경로는 /srv 로 사용

FROM python:3.12-slim

# ✅ 컨테이너 내부 기준 경로: /srv
WORKDIR /srv

# ✅ 레포에 있는 서버 소스 폴더를 컨테이너로 복사
COPY . /srv/zero-to-agile-ai-server/

# ✅ 서버 소스 폴더로 이동
WORKDIR /srv/zero-to-agile-ai-server

# ✅ 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 외부 포트(컨테이너 내부)
EXPOSE 8000

# ✅ FastAPI 실행 (app/main.py 안의 app 객체)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
