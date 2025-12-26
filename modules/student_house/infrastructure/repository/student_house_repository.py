from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidateQuery,
    StudentHouseCandidateRaw,
    StudentHouseScoreResult,
)
from modules.student_house.application.port_out.student_house_repository_port import (
    StudentHouseRepositoryPort,
)
from modules.student_house.infrastructure.orm.student_house_orm import (
    StudentHouseORM,
)
from modules.student_house.infrastructure.repository.session_helper import (
    open_session,
)


class StudentHouseRepository(StudentHouseRepositoryPort):
    """student_house 저장소 구현체."""

    STATUS_READY = "READY"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def upsert_score(
        self, house_platform_id: int, score: StudentHouseScoreResult
    ) -> int:
        """스코어 결과를 업서트하고 student_house_id를 반환한다."""
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
                self._apply_score(existing, score)
                student_house_id = existing.student_house_id
            else:
                payload = {
                    "house_platform_id": house_platform_id,
                    "price_score": score.price_score,
                    "option_score": score.option_score,
                    "risk_score": score.risk_score,
                    "base_total_score": score.base_total_score,
                    "is_student_recommended": score.is_student_recommended,
                    "processing_status": self.STATUS_COMPLETED,
                    "last_error": None,
                    "last_error_at": None,
                }
                obj = StudentHouseORM(**payload)
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
        """실패 상태를 기록한다."""
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
                        base_total_score=0.0,
                        is_student_recommended=False,
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

    def fetch_candidates(
        self, query: StudentHouseCandidateQuery
    ) -> Sequence[StudentHouseCandidateRaw]:
        """추천 후보군 원본 데이터를 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            rows = (
                session.query(StudentHouseORM, HousePlatformORM)
                .join(
                    HousePlatformORM,
                    HousePlatformORM.house_platform_id
                    == StudentHouseORM.house_platform_id,
                )
                .filter(StudentHouseORM.processing_status == self.STATUS_COMPLETED)
                .filter(StudentHouseORM.is_student_recommended.is_(True))
                .filter(
                    or_(
                        HousePlatformORM.is_banned.is_(False),
                        HousePlatformORM.is_banned.is_(None),
                    )
                )
                .order_by(StudentHouseORM.base_total_score.desc())
                .limit(query.limit)
                .all()
            )
            return [self._to_candidate(*row) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def _apply_score(
        self, target: StudentHouseORM, score: StudentHouseScoreResult
    ) -> None:
        """기존 레코드에 점수/상태를 반영한다."""
        target.price_score = score.price_score
        target.option_score = score.option_score
        target.risk_score = score.risk_score
        target.base_total_score = score.base_total_score
        target.is_student_recommended = score.is_student_recommended
        target.processing_status = self.STATUS_COMPLETED
        target.last_error = None
        target.last_error_at = None

    @staticmethod
    def _to_candidate(
        student_house: StudentHouseORM, house: HousePlatformORM
    ) -> StudentHouseCandidateRaw:
        lat, lng = _extract_lat_lng(house.lat_lng)
        return StudentHouseCandidateRaw(
            house_platform_id=student_house.house_platform_id,
            base_total_score=float(student_house.base_total_score),
            lat=lat,
            lng=lng,
        )


def _extract_lat_lng(
    lat_lng: dict | None,
) -> tuple[float | None, float | None]:
    if not lat_lng or not isinstance(lat_lng, dict):
        return None, None
    lat = lat_lng.get("lat")
    lng = lat_lng.get("lng")
    try:
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None, None
