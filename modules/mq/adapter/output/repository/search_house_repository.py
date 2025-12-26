"""
Outbound Adapter (Persistence)
- DB Session을 주입받아 search_house 테이블 CRUD 수행
- 엔진/세션 생성 금지 (infrastructure/db/postgres.py 책임)
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.orm.search_house import SearchHouse


class SearchHouseRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    # job 생성
    def create_pending(self, finder_request_id: int) -> int:
        """
        Producer Step 1:
        - search_house row 생성 (PENDING)
        - 생성된 search_house_id 반환
        """
        entity = SearchHouse(
            finder_request_id=finder_request_id,
            status="PENDING",
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity.search_house_id

    # job 접수 완료
    def mark_queued(self, search_house_id: int) -> None:
        """
        Producer Step 2:
        - MQ 발행 성공 이후 QUEUED로 전환
        """
        self.db.query(SearchHouse).filter(
            SearchHouse.search_house_id == search_house_id
        ).update({"status": "QUEUED"})
        self.db.commit()

    # worker가 job을 잡음
    def mark_processing(self, search_house_id: int) -> int:
        """
        QUEUED -> PROCESSING
        rowcount를 반환해야 execute()에서 중복처리 방지가 정상 동작함
        """
        q = (
            self.db.query(SearchHouse)
            .filter(SearchHouse.search_house_id == search_house_id)
            .filter(SearchHouse.status == "QUEUED")
        )
        updated = q.update(
            {
                "status": "PROCESSING",
                "updated_at": func.now(),
            },
            synchronize_session=False,
        )
        self.db.commit()
        return updated

    # job 산출물 저장
    def save_result(self, search_house_id: int, result: dict):
        self.db.query(SearchHouse).filter(
            SearchHouse.search_house_id == search_house_id
        ).update({
            "result_json": result,
            "completed_at": datetime.utcnow()
        })
        self.db.commit()

    # job 성공 종료, B가 메시지를 받았다는 ACK를 받으면 호출
    def mark_completed(self, search_house_id: int):
        self.db.query(SearchHouse).filter(
            SearchHouse.search_house_id == search_house_id
        ).update({"status": "COMPLETED"})
        self.db.commit()

    # job 실패 종료
    def mark_failed(self, search_house_id: int):
        self.db.query(SearchHouse).filter(
            SearchHouse.search_house_id == search_house_id
        ).update({
            "status": "FAILED"
        })
        self.db.commit()

    def get_by_id(self, search_house_id: int):
        return (
            self.db.query(SearchHouse)
            .filter(SearchHouse.search_house_id == search_house_id)
            .one_or_none()
        )