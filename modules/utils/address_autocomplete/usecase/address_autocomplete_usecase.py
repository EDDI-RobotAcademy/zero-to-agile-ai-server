from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text


class AddressAutocompleteUseCase:
    """
    입력된 prefix(예: '서', '서울', '서울특')로
    address.name 컬럼을 ILIKE prefix% 로 조회하는 유즈케이스.
    """
    def __init__(self, db: Session):
        self.db = db

    def execute(self, prefix: str) -> List[str]:
        # prefix가 완전 공백이면 그냥 빈 리스트 반환
        if not prefix:
            return []

        sql = text("""
            SELECT bjdong_full_nm
            FROM bjdong_cd_mgm
            WHERE bjdong_full_nm LIKE :pattern
            ORDER BY bjdong_full_nm
        """)

        rows = self.db.execute(sql, {"pattern": f"{prefix}%"}).scalars().all()
        return rows