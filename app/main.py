from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from modules.auth.adapter.input.web.auth_router import router as auth_router
from modules.finder_request.adapter.input.web.router.finder_request_router import router as finder_request_router
from modules.mq.adapter.input.web.router.search_house_router import router as search_house_router
from modules.utils.address_autocomplete.router.address_autocomplete_router import router as address_autocomplete
from modules.observations_assistance.adapter.input.router.building_ledger_batch_router import router as building_ledger_batch_router
from modules.house_analysis.adapter.input.web.router.house_analysis_router import router as house_analysis_router
from modules.chatbot.adapter.input.web.router.chat_router import router as chat_router
from modules.abang_user.adapter.input.web.router.abang_user_router import router as abang_user_router
from modules.university.adapter.input.web.router.university_router import router as university_router
from modules.house_platform.adapter.input.web.router.house_platform_router import router as house_platform_router
from modules.send_message.adapter.input.web.router.send_message_router import router as send_message_router
from modules.owner_recommendation.adapter.input.web.router.owner_recommendation_router import (
    router as owner_recommendation_router,
)
from modules.recommendations.adapter.input.web.router.recommendations_router import (
    router as recommendations_router,
)

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
# api_router.include_router(모듈_router) 예시 (/api + /auth = /api/auth)
api_router.include_router(auth_router)

api_router.include_router(search_house_router)
api_router.include_router(address_autocomplete)
api_router.include_router(building_ledger_batch_router)
api_router.include_router(chat_router)
api_router.include_router(abang_user_router)
api_router.include_router(university_router)
api_router.include_router(house_platform_router)
api_router.include_router(send_message_router)
api_router.include_router(owner_recommendation_router)
api_router.include_router(finder_request_router)
api_router.include_router(recommendations_router)

# 등록한 /api 라우터를 메인 앱에 연결합니다.
app.include_router(api_router)

app.include_router(house_analysis_router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run(app, host=host, port=port)