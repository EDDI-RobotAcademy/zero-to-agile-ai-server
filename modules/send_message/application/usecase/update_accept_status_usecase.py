from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.send_message.domain.send_message import SendMessage
from modules.send_message.application.dto.send_message_dto import AcceptStatusUpdateRequest

class UpdateAcceptStatusUseCase:
    def __init__(self, repository: SendMessageRepository):
        self.repository = repository

    def execute(self, user_id: int, send_message_id: int, request: AcceptStatusUpdateRequest) -> SendMessage:
        message = self.repository.find_by_id(send_message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.receiver_id != user_id:
             raise PermissionError("Only the receiver can update the acceptance status")

        message.accept_type = request.accept_type
        return self.repository.save(message)
