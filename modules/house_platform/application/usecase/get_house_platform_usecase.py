from typing import List, Optional
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.house_platform.domain.house_platform import HousePlatform
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort

class GetHousePlatformUseCase:
    def __init__(
        self, 
        repository: HousePlatformRepositoryPort,
        message_repository: SendMessageRepository = None,
        user_repository: AbangUserRepositoryPort = None
    ):
        self.repository = repository
        self.message_repository = message_repository
        self.user_repository = user_repository

    def execute_get_by_id(self, house_platform_id: int, viewer_id: int = None) -> Optional[HousePlatform]:
        house = self.repository.find_by_id(house_platform_id)
        if not house:
            return None
            
        if viewer_id and self.message_repository and self.user_repository:
            # FINDER가 HousePlatform 조회 중
            # "FINDER가 수락한 house_platform" => "OWNER가 FINDER에게 제안을 보냈고(SendMessage), FINDER가 수락(Y)"
            # sender=OWNER(writer), receiver=FINDER(viewer), house_id=house_platform_id, accept_type='Y'
            # OR "FINDER가 먼저 연락?" -> 현재 기획: OWNER -> FINDER (제안).
            # 따라서 sender=house.abang_user_id, receiver=viewer_id, house_id=house_platform_id, accept_type='Y'
            
            # 1. Check messages received by viewer from house owner
            messages = self.message_repository.find_by_receiver_id(viewer_id)
            has_accepted = any(
                m.house_platform_id == house_platform_id 
                and m.sender_id == house.abang_user_id 
                and m.accept_type == 'Y' 
                for m in messages
            )
            
            # 본인 글이면 보임
            if viewer_id == house.abang_user_id:
                has_accepted = True

            if has_accepted:
                owner = self.user_repository.find_by_id(house.abang_user_id)
                if owner:
                    setattr(house, 'phone_number', owner.phone_number)
        
        return house

    def execute_get_all_by_user(self, user_id: int) -> List[HousePlatform]:
        return self.repository.find_all_by_user_id(user_id)
