import requests
from modules.observations_assistance.application.port_out.building_ledger_external_port import BuildingLedgerExternalPort
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo" # 건축물대장 표제부 조회

class BuildingLedgerExternalClient(BuildingLedgerExternalPort):

    def __init__(self):
        self.service_key = os.getenv("SERVICE_KEY")
        if not self.service_key:
            raise EnvironmentError("API_SERVICE_KEY가 없습니다.")

    def get_br_title_info(self, **params) -> dict:
        query = {
            "serviceKey": self.service_key,
            "_type": "json",
            **params,
        }

        res = requests.get(BASE_URL, params=query, timeout=5)
        res.raise_for_status()
        return res.json()