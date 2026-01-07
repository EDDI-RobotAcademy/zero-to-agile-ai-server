from typing import List, Optional
from sqlalchemy.orm import Session
from modules.house_platform.application.port.output.house_platform_repository import HousePlatformRepository
from modules.house_platform.domain.house_platform import HousePlatform
from modules.house_platform.infrastructure.orm.house_platform_orm import HousePlatformORM

class HousePlatformRepositoryImpl(HousePlatformRepository):
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def _to_domain(self, orm: HousePlatformORM) -> HousePlatform:
        return HousePlatform(
            house_platform_id=orm.house_platform_id,
            title=orm.title,
            address=orm.address,
            deposit=orm.deposit,
            domain_id=orm.domain_id,
            rgst_no=orm.rgst_no,
            sales_type=orm.sales_type,
            monthly_rent=orm.monthly_rent,
            room_type=orm.room_type,
            contract_area=float(orm.contract_area) if orm.contract_area is not None else None,
            exclusive_area=float(orm.exclusive_area) if orm.exclusive_area is not None else None,
            floor_no=orm.floor_no,
            all_floors=orm.all_floors,
            lat_lng=orm.lat_lng,
            manage_cost=orm.manage_cost,
            can_park=orm.can_park,
            has_elevator=orm.has_elevator,
            image_urls=orm.image_urls,
            pnu_cd=orm.pnu_cd,
            is_banned=orm.is_banned,
            residence_type=orm.residence_type,
            gu_nm=orm.gu_nm,
            dong_nm=orm.dong_nm,
            registered_at=orm.registered_at,
            crawled_at=None, # ORM doesn't have crawled_at
            snapshot_id=orm.snapshot_id,
            abang_user_id=orm.abang_user_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    def save(self, house_platform: HousePlatform) -> HousePlatform:
        db: Session = self.db_session_factory()
        try:
            if house_platform.house_platform_id:
                orm = db.query(HousePlatformORM).filter(HousePlatformORM.house_platform_id == house_platform.house_platform_id).first()
                if orm:
                    orm.title = house_platform.title
                    orm.address = house_platform.address
                    orm.deposit = house_platform.deposit
                    orm.domain_id = house_platform.domain_id
                    orm.rgst_no = house_platform.rgst_no
                    orm.sales_type = house_platform.sales_type
                    orm.monthly_rent = house_platform.monthly_rent
                    orm.room_type = house_platform.room_type
                    orm.contract_area = house_platform.contract_area
                    orm.exclusive_area = house_platform.exclusive_area
                    orm.floor_no = house_platform.floor_no
                    orm.all_floors = house_platform.all_floors
                    orm.lat_lng = house_platform.lat_lng
                    orm.manage_cost = house_platform.manage_cost
                    orm.can_park = house_platform.can_park
                    orm.has_elevator = house_platform.has_elevator
                    orm.image_urls = house_platform.image_urls
                    orm.pnu_cd = house_platform.pnu_cd
                    orm.is_banned = house_platform.is_banned
                    orm.residence_type = house_platform.residence_type
                    orm.gu_nm = house_platform.gu_nm
                    orm.dong_nm = house_platform.dong_nm
                    orm.snapshot_id = house_platform.snapshot_id
                    # abang_user_id should not change typically, but strictly speaking update mirrors domain state
                    # orm.abang_user_id = house_platform.abang_user_id 
                    db.commit()
                    db.refresh(orm)
                    return self._to_domain(orm)
            
            # Create
            orm = HousePlatformORM(
                title=house_platform.title,
                address=house_platform.address,
                deposit=house_platform.deposit,
                domain_id=house_platform.domain_id,
                rgst_no=house_platform.rgst_no,
                sales_type=house_platform.sales_type,
                monthly_rent=house_platform.monthly_rent,
                room_type=house_platform.room_type,
                contract_area=house_platform.contract_area,
                exclusive_area=house_platform.exclusive_area,
                floor_no=house_platform.floor_no,
                all_floors=house_platform.all_floors,
                lat_lng=house_platform.lat_lng,
                manage_cost=house_platform.manage_cost,
                can_park=house_platform.can_park,
                has_elevator=house_platform.has_elevator,
                image_urls=house_platform.image_urls,
                pnu_cd=house_platform.pnu_cd,
                is_banned=house_platform.is_banned,
                residence_type=house_platform.residence_type,
                gu_nm=house_platform.gu_nm,
                dong_nm=house_platform.dong_nm,
                snapshot_id=house_platform.snapshot_id,
                abang_user_id=house_platform.abang_user_id
            )
            db.add(orm)
            db.commit()
            db.refresh(orm)
            return self._to_domain(orm)
        finally:
            db.close()

    def find_by_id(self, house_platform_id: int) -> Optional[HousePlatform]:
        db: Session = self.db_session_factory()
        try:
            orm = db.query(HousePlatformORM).filter(HousePlatformORM.house_platform_id == house_platform_id).first()
            if orm:
                return self._to_domain(orm)
            return None
        finally:
            db.close()

    def find_all_by_user_id(self, abang_user_id: int) -> List[HousePlatform]:
        db: Session = self.db_session_factory()
        try:
            orms = db.query(HousePlatformORM).filter(HousePlatformORM.abang_user_id == abang_user_id).all()
            return [self._to_domain(orm) for orm in orms]
        finally:
            db.close()
            
    def delete(self, house_platform_id: int) -> bool:
        db: Session = self.db_session_factory()
        try:
            orm = db.query(HousePlatformORM).filter(HousePlatformORM.house_platform_id == house_platform_id).first()
            if orm:
                db.delete(orm)
                db.commit()
                return True
            return False
        finally:
            db.close()
