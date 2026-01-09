from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.house_platform.application.dto.house_platform_dto import HousePlatformCreateRequest
from modules.house_platform.domain.house_platform import HousePlatform

class CreateHousePlatformUseCase:
    def __init__(self, repository: HousePlatformRepositoryPort):
        self.repository = repository

    def execute(self, user_id: int, request: HousePlatformCreateRequest) -> HousePlatform:
        # Create domain entity from request
        new_house = HousePlatform(
            house_platform_id=None,
            title=request.title,
            address=request.address,
            deposit=request.deposit,
            domain_id=request.domain_id,
            rgst_no=request.rgst_no,
            sales_type=request.sales_type,
            monthly_rent=request.monthly_rent,
            room_type=request.room_type,
            contract_area=request.contract_area,
            exclusive_area=request.exclusive_area,
            floor_no=request.floor_no,
            all_floors=request.all_floors,
            lat_lng=request.lat_lng,
            manage_cost=request.manage_cost,
            can_park=request.can_park,
            has_elevator=request.has_elevator,
            image_urls=request.image_urls,
            pnu_cd=request.pnu_cd,
            is_banned=request.is_banned,
            residence_type=request.residence_type,
            gu_nm=request.gu_nm,
            dong_nm=request.dong_nm,
            snapshot_id=request.snapshot_id,
            abang_user_id=user_id,
            registered_at=None,
            crawled_at=None,
            created_at=None,
            updated_at=None
        )
        return self.repository.save(new_house)
