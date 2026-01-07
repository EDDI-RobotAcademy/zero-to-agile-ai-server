from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.send_message.application.dto.send_message_dto import SendMessageCreateRequest
from modules.send_message.domain.send_message import SendMessage
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort
from modules.house_platform.application.port.output.house_platform_repository import HousePlatformRepository
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository

class CreateSendMessageUseCase:
    def __init__(
        self, 
        repository: SendMessageRepository,
        user_repository: AbangUserRepositoryPort,
        house_repository: HousePlatformRepository,
        finder_request_repository: FinderRequestRepository
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.house_repository = house_repository
        self.finder_request_repository = finder_request_repository

    def execute(self, sender_id: int, request: SendMessageCreateRequest) -> SendMessage:
        # 1. Determine Sender Type
        sender_user = self.user_repository.find_by_id(sender_id)
        if not sender_user:
            raise ValueError(f"User not found: {sender_id}")
        
        user_type = sender_user.user_type # 'FINDER' or 'OWNER'

        receiver_id = None

        # 2. Validation & Receiver Resolution
        if user_type == 'FINDER':
            # Sender is FINDER (Renter)
            # Check if finder_request belongs to sender
            finder_req = self.finder_request_repository.find_by_id(request.finder_request_id)
            if not finder_req:
                raise ValueError("Finder Request not found")
            if finder_req.abang_user_id != sender_id:
                raise PermissionError("Finder Request does not belong to sender")
            
            # Check target house and get owner (Receiver)
            house = self.house_repository.find_by_id(request.house_platform_id)
            if not house:
                raise ValueError("House Platform not found")
            
            receiver_id = house.abang_user_id
            
        elif user_type == 'OWNER':
            # Sender is OWNER (Landlord)
            # Check if house belongs to sender
            house = self.house_repository.find_by_id(request.house_platform_id)
            if not house:
                raise ValueError("House Platform not found")
            if house.abang_user_id != sender_id:
                raise PermissionError("House Platform does not belong to sender")
                
            # Check target finder request and get renter (Receiver)
            finder_req = self.finder_request_repository.find_by_id(request.finder_request_id)
            if not finder_req:
                raise ValueError("Finder Request not found")
            
            receiver_id = finder_req.abang_user_id
            
        else:
            raise ValueError("Invalid User Type for sending messages")

        if receiver_id is None:
             raise ValueError("Could not determine receiver")

        # 3. Create Message
        new_message = SendMessage(
            send_message_id=None,
            house_platform_id=request.house_platform_id,
            finder_request_id=request.finder_request_id,
            accept_type='W',
            message=request.message,
            receiver_id=receiver_id,
            sender_id=sender_id
        )
        
        return self.repository.save(new_message)
