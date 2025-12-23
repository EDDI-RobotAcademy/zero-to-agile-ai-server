from __future__ import annotations

import json
from dataclasses import asdict
from typing import Iterable, Sequence, Set

from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformManagementUpsertModel,
    HousePlatformOptionUpsertModel,
    HousePlatformUpsertModel,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)
from modules.house_platform.infrastructure.orm.house_platform_management_orm import (
    HousePlatformManagementORM,
)
from modules.house_platform.infrastructure.orm.house_platform_options_orm import (
    HousePlatformOptionORM,
)
from modules.house_platform.infrastructure.orm.house_platform_orm import HousePlatformORM


class HousePlatformRepository(HousePlatformRepositoryPort):
    """house_platform 및 부속 테이블 저장소 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session()

    def exists_rgst_nos(self, rgst_nos: Iterable[str]) -> Set[str]:
        """이미 저장된 rgst_no를 조회한다."""
        session: Session = self._session_factory()
        try:
            rows = (
                session.query(HousePlatformORM.rgst_no)
                .filter(HousePlatformORM.rgst_no.in_(list(rgst_nos)))
                .all()
            )
            return {row[0] for row in rows}
        finally:
            session.close()

    def upsert_batch(self, bundles: Sequence[HousePlatformUpsertBundle]) -> int:
        """매물/관리비/옵션을 묶어 업서트한다."""
        session: Session = self._session_factory()
        stored = 0
        try:
            for bundle in bundles:
                payload = self._to_house_platform_payload(bundle.house_platform)
                rgst_no = payload.get("rgst_no")
                if not rgst_no:
                    continue
                existing = (
                    session.query(HousePlatformORM)
                    .filter(HousePlatformORM.rgst_no == rgst_no)
                    .one_or_none()
                )
                if existing:
                    self._apply_house_platform_updates(existing, payload)
                    house_platform_id = existing.house_platform_id
                else:
                    payload = self._drop_none(payload)
                    payload.pop("house_platform_id", None)
                    obj = HousePlatformORM(**payload)
                    session.add(obj)
                    session.flush()
                    house_platform_id = obj.house_platform_id

                if bundle.management:
                    self._upsert_management(
                        session, house_platform_id, bundle.management
                    )
                if bundle.options is not None:
                    self._replace_options(
                        session, house_platform_id, bundle.options
                    )
                stored += 1
            session.commit()
            return stored
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _to_house_platform_payload(self, model: HousePlatformUpsertModel) -> dict:
        """DTO를 ORM 저장용 dict로 변환한다."""
        data = asdict(model)
        if data.get("domain_id") is not None:
            data["domain_id"] = int(data["domain_id"])
        if data.get("pnu_cd") is not None and not isinstance(data.get("pnu_cd"), int):
            try:
                data["pnu_cd"] = int(data["pnu_cd"])
            except (TypeError, ValueError):
                data["pnu_cd"] = None
        if data.get("image_urls") is not None and not isinstance(
            data.get("image_urls"), str
        ):
            data["image_urls"] = json.dumps(
                data["image_urls"], ensure_ascii=False
            )
        return data

    @staticmethod
    def _drop_none(payload: dict) -> dict:
        return {k: v for k, v in payload.items() if v is not None}

    @staticmethod
    def _apply_house_platform_updates(target: HousePlatformORM, payload: dict) -> None:
        """기존 레코드의 변경 가능한 필드만 반영한다."""
        for key, value in payload.items():
            if key in {"house_platform_id", "created_at"}:
                continue
            if value is None:
                continue
            setattr(target, key, value)

    def _upsert_management(
        self,
        session: Session,
        house_platform_id: int,
        model: HousePlatformManagementUpsertModel,
    ) -> None:
        """관리비 포함/제외 정보를 단건 업서트한다."""
        payload = asdict(model)
        payload["house_platform_id"] = house_platform_id
        existing = (
            session.query(HousePlatformManagementORM)
            .filter(
                HousePlatformManagementORM.house_platform_id == house_platform_id
            )
            .one_or_none()
        )
        if existing:
            for key, value in payload.items():
                if key in {"house_platform_management_id", "created_at"}:
                    continue
                if value is None:
                    continue
                setattr(existing, key, value)
        else:
            payload = self._drop_none(payload)
            payload.pop("house_platform_management_id", None)
            session.add(HousePlatformManagementORM(**payload))

    @staticmethod
    def _replace_options(
        session: Session,
        house_platform_id: int,
        options: Sequence[HousePlatformOptionUpsertModel],
    ) -> None:
        """옵션 목록을 전체 교체 방식으로 갱신한다."""
        session.query(HousePlatformOptionORM).filter(
            HousePlatformOptionORM.house_platform_id == house_platform_id
        ).delete(synchronize_session=False)
        rows = []
        for opt in options:
            if not opt.option:
                continue
            rows.append(
                HousePlatformOptionORM(
                    house_platform_id=house_platform_id,
                    option=str(opt.option),
                )
            )
        if rows:
            session.add_all(rows)
