from abc import ABC, abstractmethod
from typing import Dict


class BuildingLedgerPort(ABC):
    """
    건축물대장 조회 Port 인터페이스
    """

    @abstractmethod
    def fetch_building_info(self, legal_code: str) -> Dict:
        """
        법정동 코드로 건축물 정보 조회

        Args:
            legal_code: 법정동 코드

        Returns:
            건축물 정보 딕셔너리
        """
        pass
