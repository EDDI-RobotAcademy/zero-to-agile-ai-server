from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# ✨ 이 줄 추가
from modules.auth.adapter.input.web.auth_router import router as auth_router
from modules.finder_request.adapter.input.web.router.finder_request_router import router as finder_request_router
from modules.chatbot.adapter.input.web.router.chatbot import router as chatbot_router
from modules.mq.adapter.input.web.router.search_house_router import router as search_house_router

load_dotenv()
app = FastAPI()

# ✅ CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 URL
    allow_credentials=True,  # 쿠키 허용 (중요!)
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 모든 API 엔드포인트는 /api prefix 아래로 통일하기 위해 api_router를 사용합니다.
api_router = APIRouter(prefix="/api")

# 모듈 라우터 등록 예시:
# 아래와 같이 각 모듈의 router(APIRouter)를 include_router로 추가해주시면 됩니다.
# api_router.include_router(모듈_router)

# ✅ auth_router를 api_router 아래에 등록 (/api + /auth = /api/auth)
api_router.include_router(auth_router)
api_router.include_router(search_house_router)

# ✅ finder_request_router를 api_router 아래에 등록 (/api + /requests = /api/requests)
api_router.include_router(finder_request_router)

# ✅ chatbot_router를 api_router 아래에 등록 (/api + /chatbot = /api/chatbot)
api_router.include_router(chatbot_router)

# 등록한 /api 라우터를 메인 앱에 연결합니다.
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run(app, host=host, port=port)
