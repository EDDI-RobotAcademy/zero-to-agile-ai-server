from abc import ABC, abstractmethod
from typing import List


class TransactionPricePort(ABC):
    """
    실거래가 조회 Port 인터페이스
    """

    @abstractmethod
    def fetch_transaction_prices(self, legal_code: str, deal_type: str) -> List:
        """
        법정동 코드와 거래 유형으로 실거래가 정보 조회

        Args:
            legal_code: 법정동 코드
            deal_type: 거래 유형 (전세, 월세 등)

        Returns:
            실거래가 정보 리스트
        """
        pass
