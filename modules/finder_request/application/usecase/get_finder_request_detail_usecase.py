from typing import Optional
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.application.dto.finder_request_dto import FinderRequestDTO
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort


class GetFinderRequestDetailUseCase:
    """
    임차인의 요구서 상세 조회 유스케이스
    """
    
    def __init__(
        self, 
        finder_request_repository: FinderRequestRepositoryPort,
        send_message_repository: SendMessageRepository,
        user_repository: AbangUserRepositoryPort
    ):
        self.finder_request_repository = finder_request_repository
        self.send_message_repository = send_message_repository
        self.user_repository = user_repository
    
    def execute(self, finder_request_id: int, viewer_id: int) -> Optional[FinderRequestDTO]:
        """
        특정 요구서의 상세 정보를 조회합니다.
        
        Args:
            finder_request_id: 요구서 ID
            viewer_id: 조회하는 사용자 ID (권한 확인용)
            
        Returns:
            요구서 상세 정보 또는 None
        """
        # Repository를 통한 조회
        finder_request = self.finder_request_repository.find_by_id(finder_request_id)
        
        # 요구서가 없으면 None 반환
        if not finder_request:
            return None
            
        phone_number = None
        # Check if viewer has an accepted proposal for this request
        # FinderRequest 작성자는 FINDER, 조회자(viewer)는 OWNER (LANDLORD)여야 함
        # 메시지 흐름: OWNER -> FINDER (제안)
        # 따라서, sender=viewer_id, receiver=finder_request.abang_user_id, request_id=finder_request_id, accept_type='Y' 인 메시지가 있는지 확인
        # 또는 FINDER -> OWNER (역제안?) -> 현재 기획상 OWNER가 FINDER에게 제안을 보냄.
        # "LANDLORD가 FINDER의 의뢰서를 보고 제안(SendMessage)을 보냄 -> FINDER가 수락(Y)"
        # 즉, sender=LANDLORD(viewer), receiver=FINDER(writer)
        
        # messages = self.send_message_repository.find_by_sender_id(viewer_id)
        # # 이 중에서 해당 finder_request_id와 관련되고 accept_type='Y'인 것이 있는지 확인
        # has_accepted = any(
        #     m.finder_request_id == finder_request_id and m.accept_type == 'Y'
        #     for m in messages
        # )
        #
        sender_messages = self.send_message_repository.find_by_sender_id(viewer_id)
        receiver_messages = self.send_message_repository.find_by_receiver_id(viewer_id)

        messages = sender_messages + receiver_messages

        has_accepted = any(
            m.finder_request_id == finder_request_id and m.accept_type == 'Y'
            for m in messages
        )
        # 만약 조회자가 작성자 본인이면 전화번호 노출 (선택사항)
        if viewer_id == finder_request.abang_user_id:
             has_accepted = True

        if has_accepted:
            writer = self.user_repository.find_by_id(finder_request.abang_user_id)
            if writer:
                phone_number = writer.phone_number
        
        # 도메인 모델 → DTO 변환
        return FinderRequestDTO(
            finder_request_id=finder_request.finder_request_id,
            abang_user_id=finder_request.abang_user_id,
            status=finder_request.status,
            preferred_region=finder_request.preferred_region,
            price_type=finder_request.price_type,
            max_deposit=finder_request.max_deposit,
            max_rent=finder_request.max_rent,
            house_type=finder_request.house_type,
            additional_condition=finder_request.additional_condition,
            university_name=finder_request.university_name,
            roomcount=finder_request.roomcount,
            bathroomcount=finder_request.bathroomcount,
            is_near=finder_request.is_near,
            aircon_yn=finder_request.aircon_yn,
            washer_yn=finder_request.washer_yn,
            fridge_yn=finder_request.fridge_yn,
            max_building_age=finder_request.max_building_age,
            created_at=finder_request.created_at,
            updated_at=finder_request.updated_at,
            phone_number=phone_number
        )
