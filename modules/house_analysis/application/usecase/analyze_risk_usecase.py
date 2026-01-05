from modules.house_analysis.application.port.address_codec_port import AddressCodecPort
from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.application.port.risk_history_port import RiskHistoryPort
from modules.house_analysis.domain.model import RiskScore
from modules.house_analysis.domain.service import calculate_risk_score, generate_risk_summary


class AnalyzeRiskUseCase:
    """
    리스크 분석 유스케이스
    """

    def __init__(
        self,
        address_codec_port: AddressCodecPort,
        building_ledger_port: BuildingLedgerPort,
        risk_history_port: RiskHistoryPort
    ):
        self.address_codec_port = address_codec_port
        self.building_ledger_port = building_ledger_port
        self.risk_history_port = risk_history_port

    def execute(self, address: str) -> RiskScore:
        """
        주소를 입력받아 리스크 분석을 수행

        Args:
            address: 분석할 주소

        Returns:
            RiskScore: 리스크 점수 도메인 모델
        """
        # 1. 주소를 법정동 코드로 변환
        address_info = self.address_codec_port.convert_to_legal_code(address)
        legal_code = address_info["legal_code"]

        # 2. 건축물 정보 조회
        building_info = self.building_ledger_port.fetch_building_info(legal_code)

        # 3. 리스크 점수 계산
        score = calculate_risk_score(building_info)

        # 4. 요약 메시지 생성
        summary = generate_risk_summary(score)

        # 5. RiskScore 도메인 모델 생성
        risk_score = RiskScore(
            score=score,
            factors=building_info,
            summary=summary
        )

        # 6. 히스토리에 저장
        self.risk_history_port.save(risk_score)

        return risk_score
