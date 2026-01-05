from abc import ABC, abstractmethod
from modules.house_analysis.domain.model import PriceScore


class PriceHistoryPort(ABC):
    """
    가격 분석 결과 저장 Port 인터페이스
    """

    @abstractmethod
    def save(self, price_score: PriceScore) -> None:
        """
        가격 분석 결과를 저장

        Args:
            price_score: 가격 점수 도메인 모델
        """
        pass
