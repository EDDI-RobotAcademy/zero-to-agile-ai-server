"""
Application UseCase (Producer flow)

1) search_house 생성: status=PENDING
2) MQ 발행: {search_house_id}
3) search_house 업데이트: status=QUEUED
"""

from modules.mq.application.port.message_queue_port import MessageQueuePort
from modules.mq.adapter.output.repository.search_house_repository import SearchHouseRepository


class EnqueueSearchHouseUseCase:
    def __init__(self, repo: SearchHouseRepository, mq: MessageQueuePort):
        self.repo = repo
        self.mq = mq

    def execute(self, finder_request_id: int) -> int:
        # (1) DB insert
        search_house_id = self.repo.create_pending(finder_request_id)

        # (2) MQ publish
        # - 여기서 예외 나면 QUEUED로 안 바뀌고 PENDING에 남는다 (추적 가능)
        self.mq.publish_search_house(search_house_id)

        # (3) DB update
        self.repo.mark_queued(search_house_id)

        return search_house_id