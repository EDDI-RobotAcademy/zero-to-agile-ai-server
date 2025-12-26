from __future__ import annotations

import json
from typing import Iterable, Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.house_platform.application.dto.embedding_dto import (
    HousePlatformEmbeddingUpsert,
    HousePlatformSemanticSource,
)
from modules.house_platform.application.port_out.house_platform_embedding_port import (
    HousePlatformEmbeddingReadPort,
    HousePlatformEmbeddingWritePort,
)
from modules.house_platform.infrastructure.orm.house_platform_embedding_orm import (
    HousePlatformEmbeddingORM,
)
from modules.house_platform.infrastructure.orm.house_platform_management_orm import (
    HousePlatformManagementORM,
)
from modules.house_platform.infrastructure.orm.house_platform_options_orm import (
    HousePlatformOptionORM,
)
from modules.house_platform.infrastructure.orm.house_platform_orm import HousePlatformORM


class HousePlatformEmbeddingRepository(
    HousePlatformEmbeddingReadPort, HousePlatformEmbeddingWritePort
):
    """house_platform 임베딩 저장소 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session()

    def fetch_all_sources(self) -> Sequence[HousePlatformSemanticSource]:
        """임베딩에 필요한 조인 데이터를 조회한다."""
        session: Session = self._session_factory()
        try:
            rows = (
                session.query(
                    HousePlatformORM,
                    HousePlatformOptionORM,
                    HousePlatformManagementORM,
                    HousePlatformEmbeddingORM,
                )
                .outerjoin(
                    HousePlatformOptionORM,
                    HousePlatformOptionORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .outerjoin(
                    HousePlatformManagementORM,
                    HousePlatformManagementORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .outerjoin(
                    HousePlatformEmbeddingORM,
                    HousePlatformEmbeddingORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .filter(
                    or_(
                        HousePlatformORM.is_banned.is_(False),
                        HousePlatformORM.is_banned.is_(None),
                    )
                )
                .all()
            )
            return [self._to_source(*row) for row in rows]
        finally:
            session.close()

    def upsert_embeddings(self, items: Iterable[HousePlatformEmbeddingUpsert]) -> int:
        """임베딩 벡터와 설명문을 업서트한다."""
        session: Session = self._session_factory()
        saved = 0
        try:
            for item in items:
                existing = (
                    session.query(HousePlatformEmbeddingORM)
                    .filter(
                        HousePlatformEmbeddingORM.house_platform_id
                        == item.house_platform_id
                    )
                    .one_or_none()
                )
                if existing:
                    existing.embedding = item.embedding
                    if item.semantic_description is not None:
                        existing.semantic_description = item.semantic_description
                else:
                    session.add(
                        HousePlatformEmbeddingORM(
                            house_platform_id=item.house_platform_id,
                            semantic_description=item.semantic_description,
                            embedding=item.embedding,
                        )
                    )
                saved += 1
            session.commit()
            return saved
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _to_source(
        self,
        house: HousePlatformORM,
        options: HousePlatformOptionORM | None,
        management: HousePlatformManagementORM | None,
        embedding: HousePlatformEmbeddingORM | None,
    ) -> HousePlatformSemanticSource:
        return HousePlatformSemanticSource(
            house_platform_id=house.house_platform_id,
            address=house.address,
            room_type=house.room_type,
            residence_type=house.residence_type,
            deposit=house.deposit,
            monthly_rent=house.monthly_rent,
            manage_cost=house.manage_cost,
            contract_area=house.contract_area,
            exclusive_area=house.exclusive_area,
            floor_no=house.floor_no,
            all_floors=house.all_floors,
            can_park=house.can_park,
            has_elevator=house.has_elevator,
            built_in=self._parse_json_list(options.built_in)
            if options
            else None,
            near_univ=options.near_univ if options else None,
            near_transport=options.near_transport if options else None,
            near_mart=options.near_mart if options else None,
            management_included=self._parse_json_list(
                management.management_included
            )
            if management
            else None,
            management_excluded=self._parse_json_list(
                management.management_excluded
            )
            if management
            else None,
            semantic_description=embedding.semantic_description
            if embedding
            else None,
        )

    @staticmethod
    def _parse_json_list(value: str | None) -> list[str] | None:
        if not value:
            return None
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item]
        except Exception:
            return None
        return None
