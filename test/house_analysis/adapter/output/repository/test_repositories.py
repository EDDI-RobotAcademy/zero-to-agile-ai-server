import pytest
from modules.house_analysis.adapter.output.repository.address_codec_repository import AddressCodecRepository
from modules.house_analysis.adapter.output.repository.building_ledger_repository import BuildingLedgerRepository
from modules.house_analysis.adapter.output.repository.transaction_price_repository import TransactionPriceRepository


def test_address_codec_repository_integration():
    """
    실제 주소 → 법정동 코드 변환 테스트
    - AddressCodecRepository의 convert_to_legal_code() 메서드 테스트
    - 실제 변환 로직 또는 Mock 데이터 사용
    """
    # Given: AddressCodecRepository 인스턴스
    repository = AddressCodecRepository()

    # When: 주소를 법정동 코드로 변환
    result = repository.convert_to_legal_code("서울시 강남구 역삼동 777")

    # Then: 법정동 코드와 주소 정보가 반환됨
    assert result is not None
    assert "legal_code" in result
    assert "address" in result
    assert len(result["legal_code"]) > 0
    assert "역삼동" in result["address"] or "강남구" in result["address"]


def test_building_ledger_repository_integration():
    """
    실제 건축물대장 API 호출 테스트
    - BuildingLedgerRepository의 fetch_building_info() 메서드 테스트
    - 실제 API 호출 또는 Mock 데이터 사용
    """
    # Given: BuildingLedgerRepository 인스턴스
    repository = BuildingLedgerRepository()

    # When: 법정동 코드로 건축물 정보 조회
    result = repository.fetch_building_info("1168010100")

    # Then: 건축물 정보가 반환됨
    assert result is not None
    assert "is_violation" in result
    assert "has_seismic_design" in result
    assert "building_age" in result
    assert isinstance(result["is_violation"], bool)
    assert isinstance(result["has_seismic_design"], bool)
    assert isinstance(result["building_age"], int)


def test_transaction_price_repository_integration():
    """
    실제 실거래가 API 호출 테스트
    - TransactionPriceRepository의 fetch_transaction_prices() 메서드 테스트
    - 실제 API 호출 또는 Mock 데이터 사용
    """
    # Given: TransactionPriceRepository 인스턴스
    repository = TransactionPriceRepository()

    # When: 법정동 코드와 거래 유형으로 실거래가 조회
    result = repository.fetch_transaction_prices("1168010100", "전세")

    # Then: 실거래가 목록이 반환됨
    assert result is not None
    assert isinstance(result, list)
    # 데이터가 있을 수도 없을 수도 있지만, 리스트 형태여야 함
    if len(result) > 0:
        assert "price" in result[0]
        assert "area" in result[0]
        assert "deal_type" in result[0]
