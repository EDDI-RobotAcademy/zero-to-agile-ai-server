from modules.mq.adapter.output.repository.search_house_repository import (
    SearchHouseRepository,
)

class GetSearchHouseStatusUseCase:
    """
    Polling 전용 유즈케이스
    - A 로직에서만 사용
    - job 상태/결과 조회
    """

    def __init__(self, db_session):
        self.repo = SearchHouseRepository(db_session)

    def execute(self, search_house_id: int) -> dict | None:
        entity = self.repo.get_by_id(search_house_id)
        if entity is None:
            return None

        return {
            "search_house_id": entity.search_house_id,
            "status": entity.status,
            "result": entity.result_json,
            "completed_at": entity.completed_at,
        }