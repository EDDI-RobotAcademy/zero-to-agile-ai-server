"""
건축물대장 데이터 저장 Repository
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from infrastructure.orm.house_bldrgst_orm import HouseBldrgst


class HouseBldrgstRepository:
    """
    HouseBldrgst 테이블에 UPSERT 수행하는 Repository
    """

    def __init__(self, session: Session):
        self.session = session

    def upsert(self, pnu_id: str, bldrgst_data: Dict[str, Any]) -> None:
        """
        PNU 기반으로 건축물대장 데이터를 UPSERT

        Args:
            pnu_id: 19자리 PNU 필지번호
            bldrgst_data: 건축물대장 데이터
                - violation_yn: 위반 건축물 여부
                - main_use_name: 주용도코드명
                - approval_date: 사용승인일
                - seismic_yn: 내진 설계 여부
        """
        # 기존 데이터 조회
        existing = self.session.query(HouseBldrgst).filter_by(pnu_id=pnu_id).first()

        if existing:
            # UPDATE
            existing.violation_yn = bldrgst_data.get("violation_yn")
            existing.main_use_name = bldrgst_data.get("main_use_name")
            existing.approval_date = bldrgst_data.get("approval_date")
            existing.seismic_yn = bldrgst_data.get("seismic_yn")
        else:
            # INSERT
            new_record = HouseBldrgst(
                pnu_id=pnu_id,
                violation_yn=bldrgst_data.get("violation_yn"),
                main_use_name=bldrgst_data.get("main_use_name"),
                approval_date=bldrgst_data.get("approval_date"),
                seismic_yn=bldrgst_data.get("seismic_yn"),
            )
            self.session.add(new_record)

        # Note: commit은 호출자(UseCase)가 수행
