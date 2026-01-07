"""
건축물대장 저장 Port 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class HouseBldrgstPort(ABC):
    """
    건축물대장 데이터를 저장하는 Port 인터페이스
    """

    @abstractmethod
    def upsert(self, pnu_id: str, bldrgst_data: Dict[str, Any]) -> None:
        """
        PNU 기반으로 건축물대장 데이터를 UPSERT

        Args:
            pnu_id: 19자리 PNU 필지번호
            bldrgst_data: 건축물대장 데이터
        """
        pass
