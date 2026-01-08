from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from modules.finder_request.adapter.output.finder_request_model import FinderRequestModel
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.owner_recommendation.application.dto.owner_recommendation_dto import (
    OwnerRecommendationRow,
)
from modules.owner_recommendation.application.port_out.owner_recommendation_repository_port import (
    OwnerRecommendationRepositoryPort,
)


class OwnerRecommendationRepositoryImpl(OwnerRecommendationRepositoryPort):
    """owner 추천 조회용 Repository 구현체."""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def fetch_recommendations(
        self, abang_user_id: int, rent_margin: int
    ) -> List[OwnerRecommendationRow]:
        db: Session = self.db_session_factory()
        try:
            query = (
                db.query(HousePlatformORM, FinderRequestModel)
                .join(
                    FinderRequestModel,
                    (
                        HousePlatformORM.sales_type == FinderRequestModel.price_type
                    )
                    & (
                        HousePlatformORM.residence_type
                        == FinderRequestModel.house_type
                    )
                    & (HousePlatformORM.monthly_rent.isnot(None))
                    & (FinderRequestModel.max_rent.isnot(None))
                    & (
                        HousePlatformORM.monthly_rent.between(
                            FinderRequestModel.max_rent - rent_margin,
                            FinderRequestModel.max_rent + rent_margin,
                        )
                    ),
                )
                .filter(HousePlatformORM.abang_user_id == abang_user_id)
                .order_by(HousePlatformORM.house_platform_id.asc())
            )

            rows = []
            for house_orm, request_orm in query.all():
                rows.append(
                    OwnerRecommendationRow(
                        house_platform_id=house_orm.house_platform_id,
                        house_title=house_orm.title,
                        house_address=house_orm.address,
                        house_sales_type=house_orm.sales_type,
                        house_residence_type=house_orm.residence_type,
                        house_monthly_rent=house_orm.monthly_rent,
                        house_deposit=house_orm.deposit,
                        house_room_type=house_orm.room_type,
                        house_gu_nm=house_orm.gu_nm,
                        house_dong_nm=house_orm.dong_nm,
                        finder_request_id=request_orm.finder_request_id,
                        finder_abang_user_id=request_orm.abang_user_id,
                        finder_price_type=request_orm.price_type,
                        finder_house_type=request_orm.house_type,
                        finder_max_rent=request_orm.max_rent,
                        finder_preferred_region=request_orm.preferred_region,
                    )
                )
            return rows
        finally:
            db.close()
