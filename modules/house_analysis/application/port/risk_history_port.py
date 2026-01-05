from abc import ABC, abstractmethod
from modules.house_analysis.domain.model import RiskScore


class RiskHistoryPort(ABC):
    """
    리스크 분석 결과 저장 Port 인터페이스
    """

    @abstractmethod
    def save(self, risk_score: RiskScore) -> None:
        """
        리스크 분석 결과를 저장

        Args:
            risk_score: 리스크 점수 도메인 모델
        """
        pass
