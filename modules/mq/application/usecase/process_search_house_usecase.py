from sqlalchemy.orm import Session
from modules.mq.adapter.output.repository.search_house_repository import SearchHouseRepository
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository


class ProcessSearchHouseUseCase:
    """
    RabbitMQ consumer가 메시지를 하나 소비했을 때,
    AI 에이전트를 실행하고 결과를 DB에 반영하는 핵심 유즈케이스
    """

    def __init__(self, db: Session, ai_agent):
        self.db = db
        self.search_house_repo = SearchHouseRepository(db)
        self.finder_request_repo = FinderRequestRepository(db)
        self.ai_agent = ai_agent

    def execute(self, search_house_id: int):
        try:
            updated = self.search_house_repo.mark_processing(search_house_id)
            if not updated:
                return

            search_house = self.search_house_repo.get_by_id(search_house_id)
            finder_request = self.finder_request_repo.find_by_id(search_house.finder_request_id)
            result = self.ai_agent.run(finder_request)

            self.search_house_repo.save_result(search_house_id, result)
            self.search_house_repo.mark_completed(search_house_id)

        except Exception:
            self.search_house_repo.mark_failed(search_house_id)
            raise