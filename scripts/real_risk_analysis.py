"""
실제 주소로 리스크 분석 수행
- 실제 API 호출로 건축물대장 데이터 가져오기
- 실제 데이터 기반 리스크 분석 (가상 데이터 사용 안함)
"""
from infrastructure.db.postgres import SessionLocal
from modules.risk_analysis.application.service.address_parser_service import AddressParserService
from modules.risk_analysis.adapter.output.external_api.building_ledger_client import (
    BuildingLedgerClient,
    BuildingLedgerNotFoundError
)
from modules.risk_analysis.application.service.risk_service import RiskAnalysisService
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo
from datetime import datetime


def analyze_real_risk(address: str, transaction_price: int = None, transaction_area: float = None):
    """
    실제 주소로 리스크 분석 수행

    Args:
        address: 전체 주소 (예: "서울특별시 강남구 역삼동 601-3")
        transaction_price: 거래가격 (만원 단위), None이면 평균가 가정
        transaction_area: 거래면적 (m²), None이면 건물 면적 사용
    """
    print("=" * 80)
    print("[ANALYSIS] 실제 리스크 분석 (Real Building Data)")
    print("=" * 80)
    print(f"\n[TARGET] 분석 대상 주소: {address}\n")

    db = SessionLocal()

    try:
        # ========================================
        # STEP 1: 주소 파싱
        # ========================================
        print("-" * 80)
        print("STEP 1: 주소 파싱")
        print("-" * 80)

        parser = AddressParserService(db)
        codes = parser.parse_address_and_get_codes(address)

        print(f"[OK] 주소 파싱 성공:")
        print(f"  - 시군구 코드: {codes.get('sigungu_cd')}")
        print(f"  - 법정동 코드: {codes.get('bjdong_cd')}")
        print(f"  - 번: {codes.get('bun')}")
        print(f"  - 지: {codes.get('ji')}")
        print(f"  - 전체 코드: {codes.get('sigungu_cd')}-{codes.get('bjdong_cd')}-{codes.get('bun')}-{codes.get('ji')}")

        # ========================================
        # STEP 2: 실제 건축물대장 API 호출
        # ========================================
        print(f"\n{'-' * 80}")
        print("STEP 2: 건축물대장 API 호출 (실제 API)")
        print("-" * 80)

        client = BuildingLedgerClient()

        # 4자리 패딩
        bun_padded = codes.get('bun').zfill(4) if codes.get('bun') else None
        ji_padded = codes.get('ji').zfill(4) if codes.get('ji') else None

        print(f"[CALL] API 호출 중...")
        print(f"  - Endpoint: {client.endpoint}")
        print(f"  - Parameters: sigunguCd={codes.get('sigungu_cd')}, bjdongCd={codes.get('bjdong_cd')}, bun={bun_padded}, ji={ji_padded}")

        api_response = client.get_building_info(
            sigungu_cd=codes.get('sigungu_cd'),
            bjdong_cd=codes.get('bjdong_cd'),
            bun=bun_padded,
            ji=ji_padded
        )

        print(f"\n[OK] 건축물대장 데이터 조회 성공:")
        print(f"  - 주소: {api_response.get('platPlc', 'N/A')}")
        print(f"  - 사용승인일: {api_response.get('useAprDay', 'N/A')}")
        print(f"  - 구조: {api_response.get('strctCdNm', 'N/A')}")
        print(f"  - 높이: {api_response.get('heit', 'N/A')} m")
        print(f"  - 총 면적: {api_response.get('totArea', 'N/A')} m²")
        print(f"  - 위반율: {api_response.get('vlRat', 'N/A')} %")
        print(f"  - 내진설계: {'적용' if api_response.get('rserthqkDsgnApplyYn') == '1' else '미적용'}")

        # ========================================
        # STEP 3: 도메인 모델 변환 (실제 데이터)
        # ========================================
        print(f"\n{'-' * 80}")
        print("STEP 3: 도메인 모델 변환 (실제 데이터 기반)")
        print("-" * 80)

        building_info = BuildingInfo(
            address=api_response.get('platPlc', address),
            approval_date=api_response.get('useAprDay', ''),
            seismic_design=api_response.get('rserthqkDsgnApplyYn') == '1',
            violation_status=api_response.get('vlRat', '0'),
            structure_type=api_response.get('strctCdNm', '')
        )

        print(f"[OK] BuildingInfo 생성:")
        print(f"  - Address: {building_info.address}")
        print(f"  - Approval Date: {building_info.approval_date}")
        print(f"  - Seismic Design: {'Yes' if building_info.seismic_design else 'No'}")
        print(f"  - Violation Status: {building_info.violation_status}%")
        print(f"  - Structure Type: {building_info.structure_type}")

        # ========================================
        # STEP 4: 거래 정보 설정
        # ========================================
        print(f"\n{'-' * 80}")
        print("STEP 4: 거래 정보 설정")
        print("-" * 80)

        # 면적은 건물 실제 면적 사용
        actual_area = float(api_response.get('totArea', 84.0))

        # 거래가격이 지정되지 않았으면 평균가 가정 (면적 기준)
        if transaction_price is None:
            # 강남구 평균 평당 가격 약 3000만원으로 가정 (3.3m² = 1평)
            pyeong = actual_area / 3.3
            transaction_price = int(pyeong * 3000)  # 만원 단위

        transaction_area = transaction_area or actual_area

        transaction_info = TransactionInfo(
            address=address,
            transaction_date=datetime.now().strftime("%Y%m%d"),
            price=transaction_price,
            area=transaction_area
        )

        print(f"[OK] TransactionInfo 생성:")
        print(f"  - Price: {transaction_info.price:,} 만원 ({transaction_info.price / 10000:.1f}억)")
        print(f"  - Area: {transaction_info.area:.2f} m² ({transaction_info.area / 3.3:.2f}평)")
        print(f"  - Date: {transaction_info.transaction_date}")

        # ========================================
        # STEP 5: 리스크 분석 수행 (실제 데이터)
        # ========================================
        print(f"\n{'-' * 80}")
        print("STEP 5: 리스크 분석 (실제 건축물대장 데이터 기반)")
        print("-" * 80)

        risk_service = RiskAnalysisService()

        # house_platform_id 생성 (주소 기반)
        house_platform_id = f"{codes.get('sigungu_cd')}{codes.get('bjdong_cd')}{bun_padded}{ji_padded}"

        risk_score = risk_service.analyze_property(
            building=building_info,
            transaction=transaction_info,
            house_platform_id=house_platform_id
        )

        # ========================================
        # 결과 출력
        # ========================================
        print(f"\n{'=' * 80}")
        print("[RESULT] 리스크 분석 결과")
        print("=" * 80)

        # 리스크 레벨에 따른 표시
        risk_symbol = {
            "LOW": "[LOW]",
            "MEDIUM": "[MEDIUM]",
            "HIGH": "[HIGH]"
        }

        print(f"\n{risk_symbol.get(risk_score.risk_level, '[-]')} 종합 리스크 등급: {risk_score.risk_level}")
        print(f"[SCORE] 총 리스크 점수: {risk_score.total_score:.2f} / 100")

        print(f"\n[DETAIL] 세부 리스크 점수:")
        print(f"  1. 위반 건축물 리스크:  {risk_score.violation_risk:.2f} 점")
        print(f"  2. 내진설계 리스크:     {risk_score.seismic_risk:.2f} 점")
        print(f"  3. 건축물 노후화 리스크: {risk_score.age_risk:.2f} 점")
        print(f"  4. 가격 이탈 리스크:     {risk_score.price_deviation_risk:.2f} 점")

        if risk_score.warnings:
            print(f"\n[WARNING]  위험 경고 사항 ({len(risk_score.warnings)}개):")
            for i, warning in enumerate(risk_score.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print(f"\n[OK] 특별한 위험 요소가 발견되지 않았습니다.")

        # 건물 연식 계산 및 표시
        if building_info.approval_date:
            approval_year = int(building_info.approval_date[:4])
            current_year = datetime.now().year
            building_age = current_year - approval_year

            print(f"\n[BUILDING] 건축물 정보:")
            print(f"  - 사용승인일: {building_info.approval_date[:4]}년 {building_info.approval_date[4:6]}월 {building_info.approval_date[6:8]}일")
            print(f"  - 건축물 연식: {building_age}년")

        print(f"\n[TRANSACTION] 거래 정보:")
        print(f"  - 거래 예상가: {transaction_info.price:,}만원 ({transaction_info.price / 10000:.1f}억)")
        print(f"  - 평당 가격: {(transaction_info.price / (transaction_info.area / 3.3)):,.0f}만원/평")

        print("\n" + "=" * 80)
        print("[OK] 실제 데이터 기반 리스크 분석 완료")
        print("=" * 80)

        return {
            "address": address,
            "building_info": building_info,
            "transaction_info": transaction_info,
            "risk_score": risk_score,
            "api_response": api_response
        }

    except BuildingLedgerNotFoundError as e:
        print(f"\n[FAIL] 건축물대장 조회 실패: {e}")
        print(f"\n[TIP] 해당 주소의 건축물 데이터가 없습니다.")
        print(f"   다른 주소를 시도하거나, 검증된 주소를 사용하세요:")
        print(f"   예: 서울특별시 강남구 역삼동 614-1")
        return None

    except Exception as e:
        print(f"\n[FAIL] 리스크 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        db.close()


if __name__ == "__main__":
    # 사용자가 지정한 주소
    target_address = "서울특별시 강남구 역삼동 601-3"

    print("[START] 리스크 분석 시작\n")

    # 실제 분석 수행
    result = analyze_real_risk(
        address=target_address,
        transaction_price=None,  # None이면 자동 계산
        transaction_area=None    # None이면 건물 면적 사용
    )

    # 결과가 없으면 대체 주소 시도
    if result is None:
        print(f"\n{'=' * 80}")
        print("[RETRY] 대체 주소로 재시도")
        print("=" * 80)

        fallback_address = "서울특별시 강남구 역삼동 614-1"
        print(f"\n검증된 주소로 재시도: {fallback_address}\n")

        result = analyze_real_risk(
            address=fallback_address,
            transaction_price=50000,  # 5억
            transaction_area=None
        )

    if result:
        print(f"\n[OK] 분석 완료! 총 리스크 점수: {result['risk_score'].total_score:.2f}")
    else:
        print(f"\n[FAIL] 리스크 분석 실패")
