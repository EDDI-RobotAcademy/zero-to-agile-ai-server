from fastapi import FastAPI, APIRouter
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 모든 API 엔드포인트는 /api prefix 아래로 통일하기 위해 api_router를 사용합니다.
api_router = APIRouter(prefix="/api")

# 모듈 라우터 등록 예시:
# 아래와 같이 각 모듈의 router(APIRouter)를 include_router로 추가해주시면 됩니다.
# api_router.include_router(모듈_router)

# 등록한 /api 라우터를 메인 앱에 연결합니다.
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run(app, host=host, port=port)
