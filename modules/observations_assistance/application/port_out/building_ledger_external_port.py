from abc import ABC, abstractmethod
from typing import Mapping, Any

class BuildingLedgerExternalPort(ABC):

    @abstractmethod
    def get_br_title_info(self, **params) -> dict:
        pass
