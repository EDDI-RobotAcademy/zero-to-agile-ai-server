from typing import List, Optional

from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.send_message.application.dto.accepted_proposal_dto import AcceptedProposalDTO

from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort

class GetAcceptedProposalsUseCase:
    def __init__(
        self,
        send_message_repository: SendMessageRepository,
        abang_user_repository: AbangUserRepositoryPort,
        house_platform_repository: HousePlatformRepositoryPort,
        finder_request_repository: FinderRequestRepositoryPort
    ):
        self.send_message_repository = send_message_repository
        self.abang_user_repository = abang_user_repository
        self.house_platform_repository = house_platform_repository
        self.finder_request_repository = finder_request_repository

    def execute(self, user_id: int) -> List[AcceptedProposalDTO]:
        # 1. Check User Type
        user = self.abang_user_repository.find_by_id(user_id)
        if not user:
            return []

        # 2. Get Accepted Messages
        messages = self.send_message_repository.find_accepted_by_receiver_id(user_id)
        
        results = []
        
        # 3. Fetch Details based on User Type
        # "FINDER가 OWNER에게 OWNER는 FINDER에게 제안을 보내는 용도"
        # "접속자가 FINDER라면 자기가 수락한 OWNER 제안 매물 목록을"
        # FINDER accepts OWNER's proposal => Target is HOUSE (HousePlatform)
        
        if user.user_type == 'TENANT': # Assuming TENANT == FINDER
            for msg in messages:
                house = self.house_platform_repository.find_by_id(msg.house_platform_id)
                if house:
                    # Map House to dict
                    house_data = {
                        "house_platform_id": house.house_platform_id,
                        "title": house.title,
                        "address": house.address,
                        "deposit": house.deposit,
                        "monthly_rent": house.monthly_rent,
                        "image_urls": house.image_urls
                    }
                    results.append(AcceptedProposalDTO(
                        send_message_id=msg.send_message_id,
                        message=msg.message,
                        accepted_at=msg.updated_at, # Assuming updated_at is acceptance time roughly
                        target_type='HOUSE',
                        target_data=house_data
                    ))
                    
        # "접속자가 owner라면 자기가 수락한 finder 의뢰서 목록을"
        # OWNER accepts FINDER's proposal => Target is REQUEST (FinderRequest)
        elif user.user_type == 'LANDLORD': # Assuming LANDLORD == OWNER
             for msg in messages:
                req = self.finder_request_repository.find_by_id(msg.finder_request_id)
                if req:
                    # Map Request to dict
                    req_data = {
                        "finder_request_id": req.finder_request_id,
                        "preferred_region": req.preferred_region,
                        "price_type": req.price_type,
                        "max_deposit": req.max_deposit,
                        "max_rent": req.max_rent,
                        "house_type": req.house_type,
                        "university_name": req.university_name
                    }
                    results.append(AcceptedProposalDTO(
                        send_message_id=msg.send_message_id,
                        message=msg.message,
                        accepted_at=msg.updated_at,
                        target_type='REQUEST',
                        target_data=req_data
                    ))
        
        return results
