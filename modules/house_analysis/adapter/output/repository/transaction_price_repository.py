"""
실거래가 API Repository 구현체
"""
import xml.etree.ElementTree as ET
import requests
import os as os_module
from dotenv import load_dotenv
from typing import List, Dict
from modules.house_analysis.application.port.transaction_price_port import TransactionPricePort

load_dotenv()


class TransactionPriceRepository(TransactionPricePort):
    """
    실거래가 정보를 조회하는 Repository
    국토교통부 실거래가 공개시스템 API 사용
    """

    def __init__(self):
        """Initialize the Transaction Price API client."""
        self.api_key = os_module.getenv("PUBLIC_DATA_API_KEY", "")
        # 아파트 매매 실거래가 API (기본)
        self.apt_trade_endpoint = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
        # 아파트 전월세 실거래가 API
        self.apt_rent_endpoint = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent"
        self.timeout = 10  # seconds

    def fetch_transaction_prices(self, legal_code: str, deal_type: str) -> List[Dict]:
        """
        법정동 코드와 거래 유형으로 실거래가 조회

        Args:
            legal_code: 법정동 코드 (10자리, 예: 1168010100)
            deal_type: 거래 유형 ("매매", "전세", "월세")

        Returns:
            List[Dict]: 실거래가 목록 [{"price": int, "area": float, "deal_type": str}, ...]
        """
        # 법정동 코드를 시군구코드로 변환 (앞 5자리)
        if len(legal_code) != 10:
            raise ValueError(f"법정동 코드는 10자리여야 합니다: {legal_code}")

        lawd_cd = legal_code[:5]  # 지역코드 (시군구코드)

        # 거래 유형에 따라 API 엔드포인트 선택
        if deal_type == "매매":
            endpoint = self.apt_trade_endpoint
        else:  # 전세, 월세
            endpoint = self.apt_rent_endpoint

        # 최근 데이터 조회 (현재 년월)
        from datetime import datetime
        deal_ymd = datetime.now().strftime("%Y%m")

        try:
            params = {
                'serviceKey': self.api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': 10,
                'pageNo': 1
            }

            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            # XML 파싱
            return self._parse_xml_response(response.text, deal_type)

        except requests.Timeout:
            return []  # 타임아웃 시 빈 리스트 반환
        except requests.RequestException:
            return []  # 요청 실패 시 빈 리스트 반환

    def _parse_xml_response(self, xml_text: str, deal_type: str) -> List[Dict]:
        """
        XML 응답을 파싱하여 실거래가 목록 추출

        Args:
            xml_text: XML 응답 텍스트
            deal_type: 거래 유형

        Returns:
            List[Dict]: 실거래가 목록
        """
        try:
            root = ET.fromstring(xml_text)

            # 에러 체크
            header = root.find('header')
            if header is not None:
                result_code = header.findtext('resultCode', '')
                if result_code != '00':
                    return []  # 에러 시 빈 리스트 반환

            # 실거래가 데이터 추출
            body = root.find('body')
            if body is None:
                return []

            items = body.find('items')
            if items is None:
                return []

            result = []
            for item in items.findall('item'):
                try:
                    if deal_type == "매매":
                        # 매매 거래: 거래금액
                        price_str = item.findtext('dealAmount', '0')
                        price = int(price_str.replace(',', '').strip()) * 10000  # 만원 → 원
                    else:
                        # 전월세: 보증금 (월세는 월세금액도 있지만 일단 보증금 사용)
                        deposit_str = item.findtext('deposit', '0')
                        price = int(deposit_str.replace(',', '').strip()) * 10000  # 만원 → 원

                    # 전용면적 (㎡)
                    area_str = item.findtext('excluUseAr', '0')
                    area = float(area_str.strip())

                    if price > 0 and area > 0:
                        result.append({
                            "price": price,
                            "area": area,
                            "deal_type": deal_type
                        })
                except (ValueError, AttributeError):
                    continue  # 파싱 실패 시 해당 항목 스킵

            return result

        except ET.ParseError:
            return []  # XML 파싱 실패 시 빈 리스트 반환
