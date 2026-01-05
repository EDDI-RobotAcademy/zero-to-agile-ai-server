from modules.house_analysis.application.port.address_codec_port import AddressCodecPort
from modules.house_analysis.application.port.transaction_price_port import TransactionPricePort
from modules.house_analysis.application.port.price_history_port import PriceHistoryPort
from modules.house_analysis.domain.model import PriceScore
from modules.house_analysis.domain.service import (
    calculate_price_per_area,
    calculate_price_score,
    generate_price_comment
)


class AnalyzePriceUseCase:
    """
    가격 분석 유스케이스
    """

    def __init__(
        self,
        address_codec_port: AddressCodecPort,
        transaction_price_port: TransactionPricePort,
        price_history_port: PriceHistoryPort
    ):
        self.address_codec_port = address_codec_port
        self.transaction_price_port = transaction_price_port
        self.price_history_port = price_history_port

    def execute(self, address: str, deal_type: str, price: float, area: float) -> PriceScore:
        """
        주소와 매물 정보를 입력받아 가격 분석을 수행

        Args:
            address: 분석할 주소
            deal_type: 거래 유형 (전세, 월세 등)
            price: 매물 가격
            area: 전용면적 (㎡)

        Returns:
            PriceScore: 가격 점수 도메인 모델
        """
        # 1. 주소를 법정동 코드로 변환
        address_info = self.address_codec_port.convert_to_legal_code(address)
        legal_code = address_info["legal_code"]

        # 2. 실거래가 정보 조회
        transaction_prices = self.transaction_price_port.fetch_transaction_prices(legal_code, deal_type)

        # 3. 해당 매물의 평당 가격 계산
        price_per_area = calculate_price_per_area(price, area)

        # 4. 지역 평균 평당 가격 계산
        if transaction_prices:
            total_price_per_area = sum(
                calculate_price_per_area(t["price"], t["area"])
                for t in transaction_prices
            )
            area_average = total_price_per_area / len(transaction_prices)
        else:
            # 데이터가 없으면 해당 매물 가격을 평균으로 사용
            area_average = price_per_area

        # 5. 가격 점수 계산
        score = calculate_price_score(price_per_area, area_average)

        # 6. 코멘트 생성
        comment = generate_price_comment(price_per_area, area_average)

        # 7. PriceScore 도메인 모델 생성
        price_score = PriceScore(
            score=score,
            comment=comment,
            metrics={
                "price_per_area": price_per_area,
                "area_average": area_average,
                "deal_type": deal_type
            }
        )

        # 8. 히스토리에 저장
        self.price_history_port.save(price_score)

        return price_score
