"""
PNU 기반 건축물대장 조회 및 저장 UseCase 테스트
"""
import pytest
from unittest.mock import Mock
from modules.house_analysis.application.usecase.fetch_bldrgst_by_pnu_usecase import (
    FetchBldrgstByPnuUseCase,
)


def test_fetch_and_store_bldrgst_usecase():
    """
    UseCase 실행 시 API 호출 후 필드 저장 및 UPSERT 전체 흐름 테스트

    Given: PNU ID와 Mock Port들
    When: FetchBldrgstByPnuUseCase.execute() 호출
    Then:
        1. BuildingLedgerPort로 API 호출
        2. 응답 데이터를 파싱하여 필요한 필드 추출
        3. HouseBldrgstPort.upsert() 호출
        4. 반환값 없음
    """
    # Given
    pnu_id = "1168010100107770000"

    # Mock BuildingLedgerPort
    building_ledger_port = Mock()
    building_ledger_port.fetch_building_info.return_value = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 10,
        "main_use": "아파트",
        "approval_date": "20100315",
        # 실제 API 응답 구조에 맞춰서
    }

    # Mock HouseBldrgstPort
    house_bldrgst_port = Mock()

    # Mock DB Session
    db_session = Mock()

    # UseCase 인스턴스 생성
    usecase = FetchBldrgstByPnuUseCase(
        building_ledger_port=building_ledger_port,
        house_bldrgst_port=house_bldrgst_port,
        db_session=db_session,
    )

    # When
    result = usecase.execute(pnu_id)

    # Then
    # 1. BuildingLedgerPort 호출 확인
    building_ledger_port.fetch_building_info.assert_called_once()
    call_args = building_ledger_port.fetch_building_info.call_args[1]
    assert call_args["legal_code"] == "1168010100"
    assert call_args["bun"] == "777"
    assert call_args["ji"] == "0"

    # 2. HouseBldrgstPort.upsert() 호출 확인
    house_bldrgst_port.upsert.assert_called_once()
    upsert_call_args = house_bldrgst_port.upsert.call_args[0]
    assert upsert_call_args[0] == pnu_id
    upsert_data = upsert_call_args[1]
    assert "violation_yn" in upsert_data
    assert "main_use_name" in upsert_data
    assert "approval_date" in upsert_data
    assert "seismic_yn" in upsert_data

    # 3. DB commit 호출 확인
    db_session.commit.assert_called_once()

    # 4. 반환값 없음 확인
    assert result is None


def test_fetch_and_store_bldrgst_usecase_no_return():
    """
    UseCase 반환값 없음 확인 (void 함수)

    Given: 정상적인 입력
    When: UseCase 실행
    Then: 반환값이 None
    """
    # Given
    pnu_id = "1168010100107770000"
    building_ledger_port = Mock()
    building_ledger_port.fetch_building_info.return_value = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 10,
        "main_use": "아파트",
        "approval_date": "20100315",
    }
    house_bldrgst_port = Mock()
    db_session = Mock()

    usecase = FetchBldrgstByPnuUseCase(
        building_ledger_port=building_ledger_port,
        house_bldrgst_port=house_bldrgst_port,
        db_session=db_session,
    )

    # When
    result = usecase.execute(pnu_id)

    # Then
    assert result is None


def test_fetch_and_store_bldrgst_usecase_with_api_failure():
    """
    BuildingLedgerPort API 실패 시 예외 처리 테스트

    Given: BuildingLedgerPort가 예외 발생
    When: UseCase 실행
    Then: 예외가 전파되고 rollback 수행
    """
    # Given
    pnu_id = "1168010100107770000"
    building_ledger_port = Mock()
    building_ledger_port.fetch_building_info.side_effect = Exception("API 호출 실패")
    house_bldrgst_port = Mock()
    db_session = Mock()

    usecase = FetchBldrgstByPnuUseCase(
        building_ledger_port=building_ledger_port,
        house_bldrgst_port=house_bldrgst_port,
        db_session=db_session,
    )

    # When & Then
    with pytest.raises(Exception, match="API 호출 실패"):
        usecase.execute(pnu_id)

    # rollback 호출 확인
    db_session.rollback.assert_called_once()

    # upsert는 호출되지 않아야 함
    house_bldrgst_port.upsert.assert_not_called()
