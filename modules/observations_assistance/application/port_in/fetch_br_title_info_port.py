from abc import ABC, abstractmethod
from modules.observations_assistance.domain.pnu_value_object import Pnu

class FetchBrTitleInfoPort(ABC):

    @abstractmethod
    def fetch_br_title_info(self, pnu: Pnu) -> dict:
        pass