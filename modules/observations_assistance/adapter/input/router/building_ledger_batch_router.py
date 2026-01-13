from fastapi import APIRouter, Depends
from sqlalchemy import text
from infrastructure.db.postgres import get_db_session
import time

from modules.observations_assistance.application.usecase.fetch_br_title_info_usecase import (
    FetchBrTitleInfoUsecase,
)
from modules.observations_assistance.adapter.output.building_ledger_external_client import BuildingLedgerExternalClient
from modules.observations_assistance.adapter.output.repository.dj_bjdrgst_repository import (
    DjBjdrgstRepository,
)

router = APIRouter()

# http://localhost:33333/api/batch >>> 이거 돌리면 배치 시작

@router.post("/batch")
def batch_process(session=Depends(get_db_session)):
    """
    house_platform 전체를 조회 → 건축물대장 API 호출 → dj_bjdrgst 저장
    """

    # Port 구현체 생성 (session은 repository에만 주입)
    external_client = BuildingLedgerExternalClient()
    repository_port = DjBjdrgstRepository(session=session)

    # 유즈케이스 생성
    usecase = FetchBrTitleInfoUsecase(
        ledger_external_port=external_client,
        repository_port=repository_port,
    )

    # 대상 조회
    rows = session.execute(
        text(
            """
            SELECT house_platform_id, pnu_cd
            FROM house_platform
            WHERE pnu_cd IS NOT NULL
            ORDER BY house_platform_id
            """
        )
    ).fetchall()

    total = len(rows)
    success = 0
    failed = []

    for row in rows:
        time.sleep(0.2)
        pnu_cd = row.pnu_cd
        hp_id = row.house_platform_id

        try:
            usecase.fetch_and_save_by_house_platform(
                pnu_cd=pnu_cd,
                house_platform_id=hp_id,
            )
            success += 1
        except Exception as e:
            failed.append({"house_platform_id": hp_id, "pnu_cd": pnu_cd, "error": str(e)})

    return {
        "total": total,
        "success": success,
        "failed_count": len(failed),
        "failed": failed[:20],  # 너무 많으면 튀니까 일부만 노출
    }