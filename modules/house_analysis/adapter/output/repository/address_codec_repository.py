"""
주소 → 법정동 코드 변환 Repository 구현체
"""
from modules.house_analysis.application.port.address_codec_port import AddressCodecPort


class AddressCodecRepository(AddressCodecPort):
    """
    주소를 법정동 코드로 변환하는 Repository

    Note: 실제 구현에서는 외부 API나 DB를 사용하지만,
    현재는 하드코딩된 샘플 데이터를 반환합니다.
    """

    def convert_to_legal_code(self, address: str) -> dict:
        """
        주소를 법정동 코드로 변환

        Args:
            address: 변환할 주소

        Returns:
            dict: legal_code와 address를 포함하는 딕셔너리
        """
        # 최소 구현: 샘플 데이터 반환
        # TODO: 실제 API 연동 또는 DB 조회 로직 구현
        return {
            "legal_code": "1168010100",
            "address": "서울시 강남구 역삼동"
        }
