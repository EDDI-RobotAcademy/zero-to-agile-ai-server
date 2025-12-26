"""
Inbound Adapter (Web)
- HTTP 요청 → UseCase 실행
- 비즈니스 로직 없음 (조립만)

*** FastAPI Dependency 실행 흐름
1. 요청 들어옴
2. get_db_session() 호출
3. db = SessionLocal()
4. router 함수 실행 (db 전달됨)
5. 응답 반환
6. finally 블록 실행
7. db.close()
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.mq.adapter.output.repository.search_house_repository import SearchHouseRepository
from modules.mq.adapter.output.repository.rabbitmq_producer import RabbitMQProducer
from modules.mq.application.usecase.enqueue_search_house import EnqueueSearchHouseUseCase
from modules.mq.adapter.input.web.request.search_house_request import SearchHouseRequest
from fastapi import HTTPException
from modules.mq.application.usecase.get_search_house_status_usecase import (
    GetSearchHouseStatusUseCase,
)


import os
from dotenv import load_dotenv

load_dotenv()

AMQP_HOST = os.getenv("AMQP_HOST")
AMQP_PORT = int(os.getenv("AMQP_PORT", "5672"))
AMQP_USER = os.getenv("AMQP_USER")
AMQP_PASSWORD = os.getenv("AMQP_PASSWORD")

router = APIRouter()


@router.post("/search_house")
def enqueue_search_house(
    req: SearchHouseRequest,
    db: Session = Depends(get_db_session),
):
    # Outbound adapters
    repo = SearchHouseRepository(db_session=db)
    mq = RabbitMQProducer(
        host=AMQP_HOST,
        port=AMQP_PORT,
        user=AMQP_USER,
        password=AMQP_PASSWORD,
    )

    # Usecase
    usecase = EnqueueSearchHouseUseCase(repo=repo, mq=mq)

    search_house_id = usecase.execute(req.finder_request_id)

    return {
        "search_house_id": search_house_id,
        "status": "QUEUED",
    }

@router.get("/search_house/{search_house_id}")
def get_search_house_status(
    search_house_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Polling API
    - 화면 로딩바 처리용
    - search_house_id(job_id) 기준 상태/결과 조회
    """
    usecase = GetSearchHouseStatusUseCase(db)
    result = usecase.execute(search_house_id)

    if result is None:
        raise HTTPException(status_code=404, detail="search_house not found")

    return result