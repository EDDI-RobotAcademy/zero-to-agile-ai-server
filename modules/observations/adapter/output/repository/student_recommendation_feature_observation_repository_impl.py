from typing import Optional, List
from sqlalchemy.orm import Session
from modules.observations.domain.model.student_recommendation_feature_observation import (
    StudentRecommendationFeatureObservation,
    ObservationMetadata,
    # feature value objects
    PriceObservationFeatures,
    DistanceObservationFeatures,
    RiskObservationFeatures,
    ConvenienceObservationFeatures,
    ObservationNotes,
)
from modules.observations.infrastructure.orm.student_recommendation_feature_observations_orm import (
    StudentRecommendationFeatureObservationORM
)
from modules.observations.application.port.observation_repository_port import ObservationRepositoryPort


class StudentRecommendationFeatureObservationRepository(ObservationRepositoryPort):
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def find_latest_by_house_id(
        self, house_id: int
    ) -> Optional[StudentRecommendationFeatureObservation]:
        db: Session = self.db_session_factory()
        try:
            orm = (
                db.query(StudentRecommendationFeatureObservationORM)
                .filter(
                    StudentRecommendationFeatureObservationORM.house_platform_id == house_id
                )
                .order_by(StudentRecommendationFeatureObservationORM.calculated_at.desc())
                .first()
            )
            return self._to_domain(orm) if orm else None
        finally:
            db.close()

    def find_history(
        self, house_id: int
    ) -> List[StudentRecommendationFeatureObservation]:
        db: Session = self.db_session_factory()
        try:
            orms = (
                db.query(StudentRecommendationFeatureObservationORM)
                .filter(
                    StudentRecommendationFeatureObservationORM.house_platform_id == house_id
                )
                .order_by(StudentRecommendationFeatureObservationORM.calculated_at.asc())
                .all()
            )
            return [self._to_domain(o) for o in orms]
        finally:
            db.close()

    def save(self, observation: StudentRecommendationFeatureObservation) -> None:
        db: Session = self.db_session_factory()
        try:
            orm = StudentRecommendationFeatureObservationORM(
                house_platform_id=observation.platform_id,
                snapshot_id=observation.snapshot_id,

                # 가격
                price_percentile=observation.가격_관측치.가격_백분위,
                price_zscore=observation.가격_관측치.가격_z점수,
                estimated_move_in_cost=observation.가격_관측치.예상_입주비용,
                monthly_cost_est=observation.가격_관측치.월_비용_추정,
                price_burden_nonlinear=observation.가격_관측치.가격_부담_비선형,

                # 위험
                risk_event_count=observation.위험_관측치.위험_사건_개수,
                risk_event_types=observation.위험_관측치.위험_사건_유형,
                risk_probability_est=observation.위험_관측치.위험_확률_추정,
                risk_severity_score=observation.위험_관측치.위험_심각도_점수,
                risk_nonlinear_penalty=observation.위험_관측치.위험_비선형_패널티,

                # 편의
                essential_option_coverage=observation.편의_관측치.필수_옵션_커버리지,
                convenience_score=observation.편의_관측치.편의_점수,

                # 메타
                observation_notes=observation.관측_메모.notes,
                observation_version=observation.메타데이터.관측치_버전,
                source_data_version=observation.메타데이터.원본_데이터_버전,

                calculated_at=observation.calculated_at,
            )

            db.add(orm)
            db.flush()  # PK 생성
            observation.id = orm.id  # Domain에 반영
            db.commit()

        finally:
            db.close()

    @staticmethod
    def _to_domain(
            orm: StudentRecommendationFeatureObservationORM
    ) -> StudentRecommendationFeatureObservation:
        return StudentRecommendationFeatureObservation(
            id=orm.id,
            platform_id=orm.house_platform_id,
            snapshot_id=orm.snapshot_id,

            가격_관측치=PriceObservationFeatures(
                가격_백분위=orm.price_percentile,
                가격_z점수=orm.price_zscore,
                예상_입주비용=orm.estimated_move_in_cost,
                월_비용_추정=orm.monthly_cost_est,
                가격_부담_비선형=orm.price_burden_nonlinear,
            ),
            위험_관측치=RiskObservationFeatures(
                위험_사건_개수=orm.risk_event_count,
                위험_사건_유형=orm.risk_event_types,
                위험_확률_추정=orm.risk_probability_est,
                위험_심각도_점수=orm.risk_severity_score,
                위험_비선형_패널티=orm.risk_nonlinear_penalty,
            ),
            편의_관측치=ConvenienceObservationFeatures(
                필수_옵션_커버리지=orm.essential_option_coverage,
                편의_점수=orm.convenience_score,
            ),
            관측_메모=ObservationNotes(notes=orm.observation_notes),
            메타데이터=ObservationMetadata(
                관측치_버전=orm.observation_version,
                원본_데이터_버전=orm.source_data_version,
            ),
            calculated_at=orm.calculated_at,
        )
