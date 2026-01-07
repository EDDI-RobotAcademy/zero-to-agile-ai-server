"""
PNU 기반 건축물대장 조회 및 저장 UseCase
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from modules.house_analysis.domain.service import parse_pnu
from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.application.port.house_bldrgst_port import HouseBldrgstPort


class FetchBldrgstByPnuUseCase:
    """
    PNU ID를 받아 건축물대장 API를 조회하고 house_bldrgst 테이블에 UPSERT하는 UseCase
    반환값 없음 (void)
    """

    def __init__(
        self,
        building_ledger_port: BuildingLedgerPort,
        house_bldrgst_port: HouseBldrgstPort,
        db_session: Session,
    ):
        self.building_ledger_port = building_ledger_port
        self.house_bldrgst_port = house_bldrgst_port
        self.db_session = db_session

    def execute(self, pnu_id: str) -> None:
        """
        PNU ID 기반 건축물대장 조회 및 저장

        Args:
            pnu_id: 19자리 PNU 필지번호

        Returns:
            None
        """
        try:
            # 1. PNU 파싱
            parsed = parse_pnu(pnu_id)
            legal_code = parsed["legal_code"]
            bun = parsed["bun"]
            ji = parsed["ji"]

            # 2. 건축물대장 API 조회
            building_info = self.building_ledger_port.fetch_building_info(
                legal_code=legal_code, bun=bun, ji=ji
            )

            # 3. 필요한 필드 추출 및 변환
            bldrgst_data = self._extract_bldrgst_fields(building_info)

            # 4. DB에 UPSERT
            self.house_bldrgst_port.upsert(pnu_id, bldrgst_data)

            # 5. Commit
            self.db_session.commit()

        except Exception as e:
            # Rollback
            self.db_session.rollback()
            raise e

    def _extract_bldrgst_fields(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        건축물대장 API 응답에서 필요한 필드만 추출

        Args:
            building_info: 건축물대장 API 응답

        Returns:
            house_bldrgst 테이블에 저장할 데이터
        """
        return {
            "violation_yn": "Y" if building_info.get("is_violation") else "N",
            "main_use_name": building_info.get("main_use"),
            "approval_date": building_info.get("approval_date"),
            "seismic_yn": "Y" if building_info.get("has_seismic_design") else "N",
        }
