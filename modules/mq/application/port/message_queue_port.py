from abc import ABC, abstractmethod


class MessageQueuePort(ABC):
    """
    Outbound Port
    - 메시지 브로커에 작업을 발행할 수 있다는 계약(인터페이스)
    """

    @abstractmethod
    def publish_search_house(self, search_house_id: int) -> None:
        """search_house 작업 메시지를 브로커에 발행한다."""
        raise NotImplementedError