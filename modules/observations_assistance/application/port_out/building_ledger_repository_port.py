from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BuildingLedgerRepositoryPort(ABC):

    @abstractmethod
    def replace_all_by_house_platform_id(
        self,
        house_platform_id: int,
        pnu_cd: str,
        items: List[Dict[str, Any]],
    ) -> None:
        """
        1) house_platform_id + pnu_cd 기준 기존 row 삭제
        2) item 리스트를 모두 insert
        """
        raise NotImplementedError