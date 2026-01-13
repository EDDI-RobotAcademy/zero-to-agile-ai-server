from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy.orm import Session

from infrastructure.db.postgres import SessionLocal
from infrastructure.db.session_helper import open_session
from modules.student_house_decision_policy.infrastructure.orm.student_house_orm import (
    StudentHouseORM,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    StudentHouseScoreQuery,
    StudentHouseScoreRecord,
    StudentHouseScoreSummary,
)
from modules.student_house_decision_policy.application.port_out.student_house_score_port import (
    StudentHouseScorePort,
)


class StudentHouseScoreRepository(StudentHouseScorePort):
    """student_house 점수 저장소 구현체."""

    STATUS_READY = "READY"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or SessionLocal

    def upsert_score(self, score: StudentHouseScoreRecord) -> int:
        session, generator = open_session(self._session_factory)
        try:
            existing = (
                session.query(StudentHouseORM)
                .filter(
                    StudentHouseORM.house_platform_id
                    == score.house_platform_id
                )
                .one_or_none()
            )
            if existing:
                self._apply_score(existing, score)
                student_house_id = existing.student_house_id
            else:
                obj = StudentHouseORM(
                    house_platform_id=score.house_platform_id,
                    price_score=score.price_score,
                    option_score=score.option_score,
                    risk_score=score.risk_score,
                    distance_score=score.distance_score,
                    base_total_score=score.base_total_score,
                    is_student_recommended=score.is_student_recommended,
                    observation_version=score.observation_version,
                    policy_version=score.policy_version,
                    processing_status=self.STATUS_COMPLETED,
                    last_error=None,
                    last_error_at=None,
                )
                session.add(obj)
                session.flush()
                student_house_id = obj.student_house_id

            session.commit()
            return int(student_house_id)
        except Exception:
            session.rollback()
            raise
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def mark_failed(self, house_platform_id: int, reason: str) -> None:
        session, generator = open_session(self._session_factory)
        try:
            existing = (
                session.query(StudentHouseORM)
                .filter(
                    StudentHouseORM.house_platform_id == house_platform_id
                )
                .one_or_none()
            )
            if existing:
                existing.processing_status = self.STATUS_FAILED
                existing.last_error = reason
                existing.last_error_at = datetime.utcnow()
            else:
                session.add(
                    StudentHouseORM(
                        house_platform_id=house_platform_id,
                        price_score=0.0,
                        option_score=0.0,
                        risk_score=0.0,
                        distance_score=0.0,
                        base_total_score=0.0,
                        is_student_recommended=False,
                        observation_version=None,
                        policy_version=None,
                        processing_status=self.STATUS_FAILED,
                        last_error=reason,
                        last_error_at=datetime.utcnow(),
                    )
                )
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def fetch_top_k(
        self, query: StudentHouseScoreQuery
    ) -> Sequence[StudentHouseScoreSummary]:
        session, generator = open_session(self._session_factory)
        try:
            q = session.query(StudentHouseORM).filter(
                StudentHouseORM.processing_status
                == self.STATUS_COMPLETED
            )
            q = q.filter(
                StudentHouseORM.base_total_score
                >= query.threshold_base_total
            )
            if query.observation_version:
                q = q.filter(
                    StudentHouseORM.observation_version
                    == query.observation_version
                )
            if query.policy_version:
                q = q.filter(
                    StudentHouseORM.policy_version == query.policy_version
                )
            rows = (
                q.order_by(StudentHouseORM.base_total_score.desc())
                .limit(query.limit)
                .all()
            )
            return [self._to_summary(row) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def fetch_by_house_platform_ids(
        self,
        house_platform_ids: Sequence[int],
        policy_version: str | None = None,
    ) -> Sequence[StudentHouseScoreSummary]:
        """매물 ID 목록으로 점수 요약을 조회한다."""
        if not house_platform_ids:
            return []
        session, generator = open_session(self._session_factory)
        try:
            query = session.query(StudentHouseORM).filter(
                StudentHouseORM.house_platform_id.in_(house_platform_ids)
            )
            if policy_version:
                query = query.filter(
                    StudentHouseORM.policy_version == policy_version
                )
            rows = query.all()
            return [self._to_summary(row) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    @staticmethod
    def _apply_score(
        target: StudentHouseORM, score: StudentHouseScoreRecord
    ) -> None:
        target.price_score = score.price_score
        target.option_score = score.option_score
        target.risk_score = score.risk_score
        target.distance_score = score.distance_score
        target.base_total_score = score.base_total_score
        target.is_student_recommended = score.is_student_recommended
        target.observation_version = score.observation_version
        target.policy_version = score.policy_version
        target.processing_status = StudentHouseScoreRepository.STATUS_COMPLETED
        target.last_error = None
        target.last_error_at = None

    @staticmethod
    def _to_summary(
        row: StudentHouseORM,
    ) -> StudentHouseScoreSummary:
        return StudentHouseScoreSummary(
            house_platform_id=row.house_platform_id,
            base_total_score=float(row.base_total_score),
            price_score=float(row.price_score),
            option_score=float(row.option_score),
            risk_score=float(row.risk_score),
            distance_score=float(row.distance_score),
            observation_version=row.observation_version,
            policy_version=row.policy_version,
        )
