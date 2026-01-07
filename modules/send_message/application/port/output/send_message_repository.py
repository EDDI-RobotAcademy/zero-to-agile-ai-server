from abc import ABC, abstractmethod
from typing import List, Optional
from modules.send_message.domain.send_message import SendMessage

class SendMessageRepository(ABC):
    @abstractmethod
    def save(self, send_message: SendMessage) -> SendMessage:
        pass

    @abstractmethod
    def find_by_id(self, send_message_id: int) -> Optional[SendMessage]:
        pass

    @abstractmethod
    def find_by_sender_id(self, sender_id: int) -> List[SendMessage]:
        pass

    @abstractmethod
    def find_by_receiver_id(self, receiver_id: int) -> List[SendMessage]:
        pass
    
    @abstractmethod
    def find_by_house_and_request(self, house_platform_id: int, finder_request_id: int) -> Optional[SendMessage]:
        pass
