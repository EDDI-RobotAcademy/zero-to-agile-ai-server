from typing import Optional
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.house_platform.application.dto.house_platform_dto import HousePlatformUpdateRequest
from modules.house_platform.domain.house_platform import HousePlatform

class UpdateHousePlatformUseCase:
    def __init__(self, repository: HousePlatformRepositoryPort):
        self.repository = repository

    def execute(self, user_id: int, house_platform_id: int, request: HousePlatformUpdateRequest) -> Optional[HousePlatform]:
        existing_house = self.repository.find_by_id(house_platform_id)
        if not existing_house:
            return None
        
        # Permission check: Ensure the house belongs to the user
        if existing_house.abang_user_id != user_id:
            raise PermissionError("User is not the owner of this house platform.")

        # Update fields if provided
        if request.title is not None: existing_house.title = request.title
        if request.address is not None: existing_house.address = request.address
        if request.deposit is not None: existing_house.deposit = request.deposit
        if request.rgst_no is not None: existing_house.rgst_no = request.rgst_no
        if request.sales_type is not None: existing_house.sales_type = request.sales_type
        if request.monthly_rent is not None: existing_house.monthly_rent = request.monthly_rent
        if request.room_type is not None: existing_house.room_type = request.room_type
        if request.contract_area is not None: existing_house.contract_area = request.contract_area
        if request.exclusive_area is not None: existing_house.exclusive_area = request.exclusive_area
        if request.floor_no is not None: existing_house.floor_no = request.floor_no
        if request.all_floors is not None: existing_house.all_floors = request.all_floors
        if request.lat_lng is not None: existing_house.lat_lng = request.lat_lng
        if request.manage_cost is not None: existing_house.manage_cost = request.manage_cost
        if request.can_park is not None: existing_house.can_park = request.can_park
        if request.has_elevator is not None: existing_house.has_elevator = request.has_elevator
        if request.image_urls is not None: existing_house.image_urls = request.image_urls
        if request.pnu_cd is not None: existing_house.pnu_cd = request.pnu_cd
        if request.is_banned is not None: existing_house.is_banned = request.is_banned
        if request.residence_type is not None: existing_house.residence_type = request.residence_type
        if request.gu_nm is not None: existing_house.gu_nm = request.gu_nm
        if request.dong_nm is not None: existing_house.dong_nm = request.dong_nm
        if request.snapshot_id is not None: existing_house.snapshot_id = request.snapshot_id
        
        return self.repository.save(existing_house)
