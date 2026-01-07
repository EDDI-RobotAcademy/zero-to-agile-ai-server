"""
PNU(필지번호) 파싱 기능 테스트

PNU 구조 (19자리):
- 법정동코드 (10자리)
- 대지구분 (1자리): 1=대지, 2=산 (건축물대장 조회 시 무시 가능)
- 본번 (4자리): 0000~9999
- 부번 (4자리): 0000~9999

예: 1168010100 1 0777 0000
    ^^^^^^^^^^   ^  ^^^^  ^^^^
    법정동코드  구분  본   부

주의: 건축물대장 API는 대지구분을 별도로 받지 않고,
     법정동코드 + 본번 + 지번만으로 조회 가능
"""
import pytest
from modules.house_analysis.domain.service import parse_pnu


def test_pnu_parser_converts_to_legal_code_and_bun_ji():
    """
    PNU ID를 법정동코드, 본번, 지번으로 파싱하는 기능 테스트
    (대지구분은 건축물대장 조회에 불필요하므로 무시)

    Given: 19자리 PNU ID (대지구분 1 = 대지)
    When: parse_pnu() 함수 호출
    Then: legal_code(10자리), bun(본번), ji(지번) 반환 (대지구분 제외)
    """
    # Given
    pnu_id = "1168010100107770000"

    # When
    result = parse_pnu(pnu_id)

    # Then
    assert result["legal_code"] == "1168010100"
    assert result["bun"] == "777"  # 앞의 0 제거
    assert result["ji"] == "0"     # 부번이 0000이면 "0"
    # 대지구분(1)은 반환하지 않음


def test_pnu_parser_with_non_zero_ji():
    """
    지번(부번)이 0이 아닌 경우 테스트

    Given: 부번이 0이 아닌 PNU ID
    When: parse_pnu() 함수 호출
    Then: 지번도 올바르게 파싱됨
    """
    # Given
    pnu_id = "1168010100107770012"

    # When
    result = parse_pnu(pnu_id)

    # Then
    assert result["legal_code"] == "1168010100"
    assert result["bun"] == "777"
    assert result["ji"] == "12"  # 앞의 0만 제거


def test_pnu_parser_with_invalid_length():
    """
    PNU ID가 19자리가 아닌 경우 예외 발생 테스트

    Given: 19자리가 아닌 PNU ID
    When: parse_pnu() 함수 호출
    Then: ValueError 발생
    """
    # Given
    invalid_pnu = "123456789"

    # When & Then
    with pytest.raises(ValueError, match="PNU ID는 19자리여야 합니다"):
        parse_pnu(invalid_pnu)
