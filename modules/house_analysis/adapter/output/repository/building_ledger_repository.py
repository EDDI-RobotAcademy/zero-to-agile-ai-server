"""
Building ledger API repository.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
import os as os_module

import requests
from dotenv import load_dotenv

from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.domain.exception import BuildingInfoNotFoundError

load_dotenv()


class BuildingLedgerRepository(BuildingLedgerPort):
    """
    Repository to fetch building ledger information.
    """

    def __init__(self):
        self.api_key = os_module.getenv("PUBLIC_DATA_API_KEY", "")
        self.endpoint = (
            "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
        )
        self.timeout = 10

    def fetch_building_info(self, legal_code: str, bun: str, ji: str) -> dict:
        """
        Fetch building info by legal code and bun/ji.
        """
        if len(legal_code) != 10:
            raise ValueError(f"legal_code must be 10 digits: {legal_code}")

        sigungu_cd = legal_code[:5]
        bjdong_cd = legal_code[5:]

        bun = str(bun).zfill(4)
        ji = str(ji).zfill(4)

        try:
            params = {
                "serviceKey": self.api_key,
                "sigunguCd": sigungu_cd,
                "bjdongCd": bjdong_cd,
                "bun": bun,
                "ji": ji,
                "numOfRows": 1,
                "pageNo": 1,
            }

            response = requests.get(
                self.endpoint,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return self._parse_xml_response(response.text)

        except requests.Timeout:
            raise BuildingInfoNotFoundError(
                f"API request timeout: {legal_code}"
            )
        except requests.RequestException as exc:
            raise BuildingInfoNotFoundError(f"API request failed: {exc}")

    def _parse_xml_response(self, xml_text: str) -> dict:
        """
        Parse XML response into building info.
        """
        try:
            root = ET.fromstring(xml_text)

            header = root.find("header")
            if header is not None:
                result_code = header.findtext("resultCode", "")
                result_msg = header.findtext("resultMsg", "")

                if result_code != "00":
                    raise BuildingInfoNotFoundError(
                        f"API error (code: {result_code}, msg: {result_msg})"
                    )

            body = root.find("body")
            if body is None:
                raise BuildingInfoNotFoundError("response body is missing")

            items = body.find("items")
            if items is None:
                raise BuildingInfoNotFoundError("response items is missing")

            item = items.find("item")
            if item is None:
                raise BuildingInfoNotFoundError("building item not found")

            vl_rat_yn = item.findtext("vlRatEstbYn", "N")
            is_violation = vl_rat_yn.upper() == "Y"

            use_apr_day = item.findtext("useAprDay", "")
            has_seismic_design = False
            if use_apr_day and len(use_apr_day) >= 4:
                year = int(use_apr_day[:4])
                has_seismic_design = year >= 1988

            building_age = 0
            if use_apr_day and len(use_apr_day) >= 4:
                year = int(use_apr_day[:4])
                current_year = datetime.now().year
                building_age = current_year - year

            main_use = item.findtext("mainPurpsCdNm", "").strip()

            return {
                "is_violation": is_violation,
                "has_seismic_design": has_seismic_design,
                "building_age": building_age,
                "main_use": main_use,
            }

        except ET.ParseError as exc:
            raise BuildingInfoNotFoundError(f"XML parse error: {exc}")
