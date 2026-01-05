import pytest
from modules.house_analysis.application.usecase.analyze_price_usecase import AnalyzePriceUseCase
from modules.house_analysis.application.port.address_codec_port import AddressCodecPort
from modules.house_analysis.application.port.transaction_price_port import TransactionPricePort
from modules.house_analysis.application.port.price_history_port import PriceHistoryPort
from modules.house_analysis.domain.model import PriceScore


# Fake Repositories for testing
class FakeAddressCodecRepository(AddressCodecPort):
    def convert_to_legal_code(self, address: str):
        return {
            "legal_code": "1168010100",
            "address": "서울시 강남구 역삼동"
        }


class FakeTransactionPriceRepository(TransactionPricePort):
    def fetch_transaction_prices(self, legal_code: str, deal_type: str):
        return [
            {
                "price": 50000000,  # 5천만원
                "area": 33.0,  # 33㎡
                "deal_type": "전세"
            },
            {
                "price": 48000000,
                "area": 30.0,
                "deal_type": "전세"
            }
        ]


class FakePriceHistoryRepository(PriceHistoryPort):
    def __init__(self):
        self.saved_price_scores = []

    def save(self, price_score: PriceScore) -> None:
        self.saved_price_scores.append(price_score)


def test_analyze_price_usecase_with_mocked_ports():
    """
    Mock Port를 사용한 가격 분석 유스케이스 테스트
    - 주소 → 법정동 코드 → 실거래가 정보 → 점수 계산 → DB 저장
    """
    # Given: Fake Repositories
    address_codec_port = FakeAddressCodecRepository()
    transaction_price_port = FakeTransactionPriceRepository()
    price_history_port = FakePriceHistoryRepository()

    # When: UseCase 실행
    usecase = AnalyzePriceUseCase(
        address_codec_port=address_codec_port,
        transaction_price_port=transaction_price_port,
        price_history_port=price_history_port
    )

    result = usecase.execute(
        address="서울시 강남구 역삼동 777",
        deal_type="전세",
        price=60000000,  # 6천만원
        area=33.0  # 33㎡
    )

    # Then: 가격 점수가 계산되었는지 확인
    # 평당 가격: 60000000 / 33 * 3.3 = 6,000,000 (600만원/평)
    # 지역 평균: (50000000/33*3.3 + 48000000/30*3.3) / 2 = (5,000,000 + 5,280,000) / 2 = 5,140,000 (514만원/평)
    # 차이: (6,000,000 - 5,140,000) / 5,140,000 * 100 = 16.7%
    # 점수: 50 - (16.7 * 0.5) = 50 - 8.35 = 41.65 ≈ 42
    assert result.score == 42
    assert "높은 가격" in result.comment

    # Then: 히스토리 저장이 호출되었는지 확인
    assert len(price_history_port.saved_price_scores) == 1
    saved_price_score = price_history_port.saved_price_scores[0]
    assert saved_price_score.score == 42


def test_analyze_price_usecase_with_no_transaction_data():
    """
    실거래가 데이터가 없는 경우 처리
    - 기본 점수 반환 또는 적절한 메시지
    """
    # Given: 실거래가 데이터가 없는 Fake Repository
    class FakeTransactionPriceRepositoryEmpty(TransactionPricePort):
        def fetch_transaction_prices(self, legal_code: str, deal_type: str):
            return []  # 빈 리스트 반환

    address_codec_port = FakeAddressCodecRepository()
    transaction_price_port = FakeTransactionPriceRepositoryEmpty()
    price_history_port = FakePriceHistoryRepository()

    # When: UseCase 실행
    usecase = AnalyzePriceUseCase(
        address_codec_port=address_codec_port,
        transaction_price_port=transaction_price_port,
        price_history_port=price_history_port
    )

    result = usecase.execute(
        address="서울시 강남구 역삼동 777",
        deal_type="전세",
        price=60000000,  # 6천만원
        area=33.0  # 33㎡
    )

    # Then: 데이터가 없을 때는 기준점 50점 반환
    # 평당 가격 = 지역 평균 (데이터 없으므로)
    # 차이 = 0% → 점수 = 50
    assert result.score == 50
    assert "평균" in result.comment or "비슷" in result.comment

    # Then: 히스토리 저장은 여전히 수행됨
    assert len(price_history_port.saved_price_scores) == 1


def test_analyze_price_usecase_with_different_deal_types():
    """
    거래 유형별(전세/월세) 가격 분석
    - 각 거래 유형에 맞는 계산 로직 적용
    """
    # Given: 월세 데이터를 반환하는 Fake Repository
    class FakeTransactionPriceRepositoryMonthly(TransactionPricePort):
        def fetch_transaction_prices(self, legal_code: str, deal_type: str):
            if deal_type == "월세":
                return [
                    {"price": 500000, "area": 33.0, "deal_type": "월세"},
                    {"price": 480000, "area": 30.0, "deal_type": "월세"}
                ]
            return []

    address_codec_port = FakeAddressCodecRepository()
    transaction_price_port = FakeTransactionPriceRepositoryMonthly()
    price_history_port = FakePriceHistoryRepository()

    # When: 월세로 UseCase 실행
    usecase = AnalyzePriceUseCase(
        address_codec_port=address_codec_port,
        transaction_price_port=transaction_price_port,
        price_history_port=price_history_port
    )

    result = usecase.execute(
        address="서울시 강남구 역삼동 777",
        deal_type="월세",
        price=600000,  # 60만원 (월세)
        area=33.0
    )

    # Then: 월세 데이터로 점수가 계산됨
    # 평당 월세: 600000 / 33 * 3.3 = 60,000
    # 지역 평균: (500000/33*3.3 + 480000/30*3.3) / 2 = (50,000 + 52,800) / 2 = 51,400
    # 차이: (60,000 - 51,400) / 51,400 * 100 = 16.7%
    # 점수: 50 - (16.7 * 0.5) = 50 - 8.35 = 41.65 ≈ 42
    assert result.score == 42
    assert result.metrics["deal_type"] == "월세"
    assert "높은 가격" in result.comment

    # Then: 히스토리 저장 확인
    assert len(price_history_port.saved_price_scores) == 1
    saved = price_history_port.saved_price_scores[0]
    assert saved.metrics["deal_type"] == "월세"
