from typing import List
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.send_message.domain.send_message import SendMessage

class GetSendMessageUseCase:
    def __init__(self, repository: SendMessageRepository):
        self.repository = repository

    def get_sent_messages(self, user_id: int) -> List[SendMessage]:
        return self.repository.find_by_sender_id(user_id)

    def get_received_messages(self, user_id: int) -> List[SendMessage]:
        return self.repository.find_by_receiver_id(user_id)
