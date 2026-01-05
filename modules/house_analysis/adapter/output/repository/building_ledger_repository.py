"""
건축물대장 API Repository 구현체
"""
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import os as os_module
from dotenv import load_dotenv
from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.domain.exception import BuildingInfoNotFoundError

load_dotenv()


class BuildingLedgerRepository(BuildingLedgerPort):
    """
    건축물대장 정보를 조회하는 Repository
    공공데이터포털 건축물대장 API 사용
    """

    def __init__(self):
        """Initialize the Building Ledger API client."""
        self.api_key = os_module.getenv("PUBLIC_DATA_API_KEY", "")
        self.endpoint = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
        self.timeout = 10  # seconds

    def fetch_building_info(self, legal_code: str) -> dict:
        """
        법정동 코드로 건축물 정보 조회

        Args:
            legal_code: 법정동 코드 (10자리, 예: 1168010100)
                       앞 5자리: 시군구코드, 뒤 5자리: 법정동코드

        Returns:
            dict: 건축물 정보 (is_violation, has_seismic_design, building_age)

        Raises:
            BuildingInfoNotFoundError: 건축물 정보를 찾을 수 없는 경우
        """
        # 법정동 코드를 시군구코드와 법정동코드로 분리
        if len(legal_code) != 10:
            raise ValueError(f"법정동 코드는 10자리여야 합니다: {legal_code}")

        sigungu_cd = legal_code[:5]  # 앞 5자리
        bjdong_cd = legal_code[5:]   # 뒤 5자리

        # 샘플 번/지 값으로 API 호출 (실제로는 주소에서 파싱해야 함)
        # 역삼동 일대의 샘플 번지 (4자리로 패딩)
        bun = "0777"
        ji = "0000"

        # API 호출
        try:
            params = {
                'serviceKey': self.api_key,
                'sigunguCd': sigungu_cd,
                'bjdongCd': bjdong_cd,
                'bun': bun,
                'ji': ji,
                'numOfRows': 1,
                'pageNo': 1
            }

            response = requests.get(
                self.endpoint,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            # XML 파싱
            return self._parse_xml_response(response.text)

        except requests.Timeout:
            raise BuildingInfoNotFoundError(f"API 요청 시간 초과: {legal_code}")
        except requests.RequestException as e:
            raise BuildingInfoNotFoundError(f"API 요청 실패: {str(e)}")

    def _parse_xml_response(self, xml_text: str) -> dict:
        """
        XML 응답을 파싱하여 필요한 정보 추출

        Args:
            xml_text: XML 응답 텍스트

        Returns:
            dict: 건축물 정보
        """
        try:
            root = ET.fromstring(xml_text)

            # 에러 체크
            header = root.find('header')
            if header is not None:
                result_code = header.findtext('resultCode', '')
                result_msg = header.findtext('resultMsg', '')

                if result_code != '00':
                    raise BuildingInfoNotFoundError(
                        f"API 에러 (코드: {result_code}, 메시지: {result_msg})"
                    )

            # 건축물 데이터 추출
            body = root.find('body')
            if body is None:
                raise BuildingInfoNotFoundError("응답에 body가 없습니다")

            items = body.find('items')
            if items is None:
                raise BuildingInfoNotFoundError("응답에 items가 없습니다")

            item = items.find('item')
            if item is None:
                raise BuildingInfoNotFoundError("건축물 데이터를 찾을 수 없습니다")

            # 필요한 필드 추출 및 변환
            # 위반 건축물 여부 (vlRat: 위반건축물 여부)
            vl_rat_yn = item.findtext('vlRatEstbYn', 'N')  # 위반건축물여부
            is_violation = vl_rat_yn.upper() == 'Y'

            # 내진 설계 여부 (qltyGradeYn: 품질등급 여부, etcRoof: 기타 지붕 등)
            # 실제로는 useAprDay(사용승인일)로 내진설계 의무화 시점 기준 판단
            use_apr_day = item.findtext('useAprDay', '')  # 사용승인일 (YYYYMMDD)

            # 1988년 이후 건물은 내진설계 의무화 (간단한 기준)
            has_seismic_design = False
            if use_apr_day and len(use_apr_day) >= 4:
                year = int(use_apr_day[:4])
                has_seismic_design = year >= 1988

            # 건물 연령 계산
            building_age = 0
            if use_apr_day and len(use_apr_day) >= 4:
                year = int(use_apr_day[:4])
                current_year = datetime.now().year
                building_age = current_year - year

            return {
                "is_violation": is_violation,
                "has_seismic_design": has_seismic_design,
                "building_age": building_age
            }

        except ET.ParseError as e:
            raise BuildingInfoNotFoundError(f"XML 파싱 실패: {str(e)}")
