from abc import ABC, abstractmethod
from typing import Dict


class AddressCodecPort(ABC):
    """
    주소 → 법정동 코드 변환 Port 인터페이스
    """

    @abstractmethod
    def convert_to_legal_code(self, address: str) -> Dict:
        """
        주소를 법정동 코드로 변환

        Args:
            address: 주소 문자열

        Returns:
            법정동 코드 정보 딕셔너리
        """
        pass
