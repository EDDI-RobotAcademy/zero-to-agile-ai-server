import pytest
from modules.house_analysis.application.usecase.analyze_risk_usecase import AnalyzeRiskUseCase
from modules.house_analysis.application.port.address_codec_port import AddressCodecPort
from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.application.port.risk_history_port import RiskHistoryPort
from modules.house_analysis.domain.model import RiskScore
from modules.house_analysis.domain.exception import InvalidAddressError, BuildingInfoNotFoundError


# Fake Repositories for testing
class FakeAddressCodecRepository(AddressCodecPort):
    def convert_to_legal_code(self, address: str):
        return {
            "legal_code": "1168010100",
            "address": "서울시 강남구 역삼동"
        }


class FakeBuildingLedgerRepository(BuildingLedgerPort):
    def fetch_building_info(self, legal_code: str):
        return {
            "is_violation": True,
            "has_seismic_design": False,
            "building_age": 35
        }


class FakeRiskHistoryRepository(RiskHistoryPort):
    def __init__(self):
        self.saved_risk_scores = []

    def save(self, risk_score: RiskScore) -> None:
        self.saved_risk_scores.append(risk_score)


def test_analyze_risk_usecase_with_mocked_ports():
    """
    Mock Port를 사용한 리스크 분석 유스케이스 테스트
    - 주소 → 법정동 코드 → 건축물 정보 → 점수 계산 → DB 저장
    """
    # Given: Fake Repositories
    address_codec_port = FakeAddressCodecRepository()
    building_ledger_port = FakeBuildingLedgerRepository()
    risk_history_port = FakeRiskHistoryRepository()

    # When: UseCase 실행
    usecase = AnalyzeRiskUseCase(
        address_codec_port=address_codec_port,
        building_ledger_port=building_ledger_port,
        risk_history_port=risk_history_port
    )

    result = usecase.execute(address="서울시 강남구 역삼동 777")

    # Then: 리스크 점수가 정확히 계산되었는지 확인
    # 위반(30) + 내진설계없음(25) + 35년(40) = 95
    assert result.score == 95
    assert result.summary == "위험도 매우 높음"
    assert result.factors["is_violation"] is True
    assert result.factors["has_seismic_design"] is False
    assert result.factors["building_age"] == 35

    # Then: 히스토리 저장이 호출되었는지 확인
    assert len(risk_history_port.saved_risk_scores) == 1
    saved_risk_score = risk_history_port.saved_risk_scores[0]
    assert saved_risk_score.score == 95
    assert saved_risk_score.summary == "위험도 매우 높음"


def test_analyze_risk_usecase_with_invalid_address():
    """
    잘못된 주소 입력 시 예외 처리
    - AddressCodecPort에서 예외 발생 → 적절한 에러 응답
    """
    # Given: 잘못된 주소를 처리하는 Fake Repository
    class FakeAddressCodecRepositoryWithError(AddressCodecPort):
        def convert_to_legal_code(self, address: str):
            raise InvalidAddressError(f"유효하지 않은 주소입니다: {address}")

    address_codec_port = FakeAddressCodecRepositoryWithError()
    building_ledger_port = FakeBuildingLedgerRepository()
    risk_history_port = FakeRiskHistoryRepository()

    # When & Then: UseCase 실행 시 InvalidAddressError 발생
    usecase = AnalyzeRiskUseCase(
        address_codec_port=address_codec_port,
        building_ledger_port=building_ledger_port,
        risk_history_port=risk_history_port
    )

    with pytest.raises(InvalidAddressError) as exc_info:
        usecase.execute(address="잘못된주소123")

    # Then: 에러 메시지 확인
    assert "유효하지 않은 주소입니다" in str(exc_info.value)


def test_analyze_risk_usecase_with_api_failure():
    """
    건축물대장 API 실패 시 예외 처리
    - BuildingLedgerPort에서 예외 발생 → 적절한 에러 응답
    """
    # Given: API 실패를 시뮬레이션하는 Fake Repository
    class FakeBuildingLedgerRepositoryWithError(BuildingLedgerPort):
        def fetch_building_info(self, legal_code: str):
            raise BuildingInfoNotFoundError(f"건축물 정보를 찾을 수 없습니다: {legal_code}")

    address_codec_port = FakeAddressCodecRepository()
    building_ledger_port = FakeBuildingLedgerRepositoryWithError()
    risk_history_port = FakeRiskHistoryRepository()

    # When & Then: UseCase 실행 시 BuildingInfoNotFoundError 발생
    usecase = AnalyzeRiskUseCase(
        address_codec_port=address_codec_port,
        building_ledger_port=building_ledger_port,
        risk_history_port=risk_history_port
    )

    with pytest.raises(BuildingInfoNotFoundError) as exc_info:
        usecase.execute(address="서울시 강남구 역삼동 777")

    # Then: 에러 메시지 확인
    assert "건축물 정보를 찾을 수 없습니다" in str(exc_info.value)
