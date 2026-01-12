from typing import List
from sqlalchemy.orm import Session

from modules.observations.application.port.price_observation_repository_port import PriceObservationRepositoryPort
from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation
from modules.observations.infrastructure.orm.student_recommendation_price_observations_orm import \
    StudentRecommendationPriceObservationsORM


class StudentRecommendationPriceObservationRepository(PriceObservationRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def save_bulk(self, observations: List[PriceFeatureObservation]) -> None:
        """여러 PriceFeatureObservation을 DB에 저장"""
        orm_objects = [
            StudentRecommendationPriceObservationsORM(
                house_platform_id=o.house_platform_id,
                recommendation_observation_id=o.recommendation_observation_id,
                가격_백분위=o.가격_백분위,
                가격_z점수=o.가격_z점수,
                예상_입주비용=o.예상_입주비용,
                월_비용_추정=o.월_비용_추정,
                가격_부담_비선형=o.가격_부담_비선형,
                calculated_at=o.calculated_at,
            )
            for o in observations
        ]
        self.session.bulk_save_objects(orm_objects)
        self.session.commit()

    def save(self, observation: PriceFeatureObservation) -> PriceFeatureObservation:
        """단일 PriceFeatureObservation 저장 및 PK 반환"""
        orm_obj = StudentRecommendationPriceObservationsORM(
            house_platform_id=observation.house_platform_id,
            recommendation_observation_id=observation.recommendation_observation_id,
            가격_백분위=observation.가격_백분위,
            가격_z점수=observation.가격_z점수,
            예상_입주비용=observation.예상_입주비용,
            월_비용_추정=observation.월_비용_추정,
            가격_부담_비선형=observation.가격_부담_비선형,
            calculated_at=observation.calculated_at,
        )
        self.session.add(orm_obj)
        self.session.commit()

        # frozen dataclass이므로 새 객체를 만들어 반환
        return PriceFeatureObservation(
            id=orm_obj.id,
            house_platform_id=observation.house_platform_id,
            recommendation_observation_id=observation.recommendation_observation_id,
            가격_백분위=observation.가격_백분위,
            가격_z점수=observation.가격_z점수,
            예상_입주비용=observation.예상_입주비용,
            월_비용_추정=observation.월_비용_추정,
            가격_부담_비선형=observation.가격_부담_비선형,
            calculated_at=observation.calculated_at,
        )
