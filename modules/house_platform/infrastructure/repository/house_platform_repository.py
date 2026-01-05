from __future__ import annotations

import json
from dataclasses import asdict
from typing import Iterable, Sequence, Set

from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from infrastructure.db.session_helper import open_session
from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformManagementUpsertModel,
    HousePlatformOptionUpsertModel,
    HousePlatformUpsertModel,
)
from modules.house_platform.application.dto.delete_house_platform_dto import (
    DeleteHousePlatformResult,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)
from modules.house_platform.application.dto.monitor_house_platform_dto import (
    HousePlatformMonitorTarget,
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
        self._session_factory = session_factory or get_db_session

    def exists_rgst_nos(self, rgst_nos: Iterable[str]) -> Set[str]:
        """이미 저장된 rgst_no를 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            rows = (
                session.query(HousePlatformORM.rgst_no)
                .filter(HousePlatformORM.rgst_no.in_(list(rgst_nos)))
                .all()
            )
            return {row[0] for row in rows}
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def upsert_batch(self, bundles: Sequence[HousePlatformUpsertBundle]) -> int:
        """매물/관리비/옵션을 묶어 업서트한다."""
        session, generator = open_session(self._session_factory)
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
                    if payload.get("is_banned") is None:
                        payload["is_banned"] = False
                    obj = HousePlatformORM(**payload)
                    session.add(obj)
                    session.flush()
                    house_platform_id = obj.house_platform_id

                if bundle.management:
                    self._upsert_management(
                        session, house_platform_id, bundle.management
                    )
                if bundle.options is not None:
                    self._upsert_options(
                        session, house_platform_id, bundle.options
                    )
                stored += 1
            session.commit()
            return stored
        except Exception:
            session.rollback()
            raise
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def soft_delete_by_id(self, house_platform_id: int) -> DeleteHousePlatformResult:
        """is_banned 플래그를 True로 설정한다."""
        session, generator = open_session(self._session_factory)
        try:
            target = (
                session.query(HousePlatformORM)
                .filter(HousePlatformORM.house_platform_id == house_platform_id)
                .one_or_none()
            )
            if not target:
                return DeleteHousePlatformResult(
                    house_platform_id=house_platform_id,
                    deleted=False,
                    message="대상 매물이 없습니다.",
                )
            if target.is_banned:
                return DeleteHousePlatformResult(
                    house_platform_id=house_platform_id,
                    deleted=False,
                    already_deleted=True,
                    message="이미 삭제 처리된 매물입니다.",
                )
            target.is_banned = True
            session.commit()
            return DeleteHousePlatformResult(
                house_platform_id=house_platform_id,
                deleted=True,
            )
        except Exception:
            session.rollback()
            raise
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def fetch_monitor_targets(
        self, updated_before, limit: int | None = None
    ) -> Sequence[HousePlatformMonitorTarget]:
        """updated_at 기준 모니터링 대상 목록을 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            query = (
                session.query(
                    HousePlatformORM.house_platform_id,
                    HousePlatformORM.domain_id,
                    HousePlatformORM.rgst_no,
                    HousePlatformORM.updated_at,
                    HousePlatformORM.is_banned,
                )
                .filter(
                    or_(
                        HousePlatformORM.updated_at <= updated_before,
                        HousePlatformORM.updated_at.is_(None),
                    )
                )
                .filter(HousePlatformORM.rgst_no.isnot(None))
                .order_by(HousePlatformORM.updated_at.asc())
            )
            if limit:
                query = query.limit(limit)
            rows = query.all()
            return [
                HousePlatformMonitorTarget(
                    house_platform_id=row[0],
                    domain_id=row[1],
                    rgst_no=row[2],
                    updated_at=row[3],
                    is_banned=row[4],
                )
                for row in rows
            ]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def fetch_bundle_by_id(
        self, house_platform_id: int
    ) -> HousePlatformUpsertBundle | None:
        """기존 저장 데이터를 번들 형태로 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            house = (
                session.query(HousePlatformORM)
                .filter(HousePlatformORM.house_platform_id == house_platform_id)
                .one_or_none()
            )
            if not house:
                return None
            management = (
                session.query(HousePlatformManagementORM)
                .filter(
                    HousePlatformManagementORM.house_platform_id
                    == house_platform_id
                )
                .one_or_none()
            )
            options = (
                session.query(HousePlatformOptionORM)
                .filter(HousePlatformOptionORM.house_platform_id == house_platform_id)
                .one_or_none()
            )
            return HousePlatformUpsertBundle(
                house_platform=self._to_house_platform_model(house),
                management=self._to_management_model(management)
                if management
                else None,
                options=self._to_options_model(options) if options else None,
            )
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def _to_house_platform_payload(self, model: HousePlatformUpsertModel) -> dict:
        """DTO를 ORM 저장용 dict로 변환한다."""
        data = asdict(model)
        if data.get("domain_id") is not None:
            data["domain_id"] = int(data["domain_id"])
        if data.get("pnu_cd") is not None and not isinstance(data.get("pnu_cd"), str):
            data["pnu_cd"] = str(data["pnu_cd"])
        if data.get("image_urls") is not None and not isinstance(
            data.get("image_urls"), str
        ):
            data["image_urls"] = json.dumps(
                data["image_urls"], ensure_ascii=False
            )
        return data

    @staticmethod
    def _to_house_platform_model(
        model: HousePlatformORM,
    ) -> HousePlatformUpsertModel:
        """ORM 데이터를 업서트 모델로 변환한다."""
        return HousePlatformUpsertModel(
            house_platform_id=model.house_platform_id,
            title=model.title,
            address=model.address,
            deposit=model.deposit,
            created_at=model.created_at,
            updated_at=model.updated_at,
            registered_at=model.registered_at,
            domain_id=model.domain_id,
            rgst_no=model.rgst_no,
            snapshot_id=model.snapshot_id,
            pnu_cd=model.pnu_cd,
            is_banned=model.is_banned,
            sales_type=model.sales_type,
            monthly_rent=model.monthly_rent,
            room_type=model.room_type,
            residence_type=model.residence_type,
            contract_area=model.contract_area,
            exclusive_area=model.exclusive_area,
            floor_no=model.floor_no,
            all_floors=model.all_floors,
            lat_lng=model.lat_lng if model.lat_lng else None,
            manage_cost=model.manage_cost,
            can_park=model.can_park,
            has_elevator=model.has_elevator,
            image_urls=_parse_json_list(model.image_urls),
            gu_nm=model.gu_nm,
            dong_nm=model.dong_nm,
        )

    @staticmethod
    def _to_management_model(
        model: HousePlatformManagementORM,
    ) -> HousePlatformManagementUpsertModel:
        """관리비 ORM을 업서트 모델로 변환한다."""
        return HousePlatformManagementUpsertModel(
            house_platform_management_id=model.house_platform_management_id,
            house_platform_id=model.house_platform_id,
            management_included=model.management_included,
            management_excluded=model.management_excluded,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_options_model(
        model: HousePlatformOptionORM,
    ) -> HousePlatformOptionUpsertModel:
        """옵션 ORM을 업서트 모델로 변환한다."""
        return HousePlatformOptionUpsertModel(
            house_platform_options_id=model.house_platform_options_id,
            house_platform_id=model.house_platform_id,
            built_in=_parse_json_list(model.built_in),
            near_univ=model.near_univ,
            near_transport=model.near_transport,
            near_mart=model.near_mart,
            nearby_pois=model.nearby_pois if model.nearby_pois else None,
        )

    @staticmethod
    def _drop_none(payload: dict) -> dict:
        return {k: v for k, v in payload.items() if v is not None}

    @staticmethod
    def _apply_house_platform_updates(target: HousePlatformORM, payload: dict) -> None:
        """기존 레코드의 변경 가능한 필드만 반영한다."""
        for key, value in payload.items():
            if key in {"house_platform_id", "created_at", "is_banned"}:
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
    def _upsert_options(
        session: Session,
        house_platform_id: int,
        options: HousePlatformOptionUpsertModel,
    ) -> None:
        """옵션/주변 정보를 한 행으로 업서트한다."""
        has_payload = any(
            value is not None
            for value in (
                options.built_in,
                options.near_univ,
                options.near_transport,
                options.near_mart,
                options.nearby_pois,
            )
        )
        if not has_payload:
            return

        payload = {
            "built_in": json.dumps(options.built_in, ensure_ascii=False)
            if options.built_in is not None
            else None,
            "near_univ": options.near_univ,
            "near_transport": options.near_transport,
            "near_mart": options.near_mart,
            "nearby_pois": options.nearby_pois,
        }

        existing = (
            session.query(HousePlatformOptionORM)
            .filter(HousePlatformOptionORM.house_platform_id == house_platform_id)
            .one_or_none()
        )
        if existing:
            for key, value in payload.items():
                if value is None:
                    continue
                setattr(existing, key, value)
        else:
            session.add(
                HousePlatformOptionORM(
                    house_platform_id=house_platform_id,
                    **{k: v for k, v in payload.items() if v is not None},
                )
            )


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
