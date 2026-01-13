import logging
from typing import Dict, Any

from modules.observations_assistance.application.port_in.fetch_br_title_info_port import FetchBrTitleInfoPort
from modules.observations_assistance.application.port_out.building_ledger_external_port import BuildingLedgerExternalPort
from modules.observations_assistance.application.port_out.building_ledger_repository_port import BuildingLedgerRepositoryPort
from modules.observations_assistance.domain.pnu_value_object import Pnu

logger = logging.getLogger(__name__)


class FetchBrTitleInfoUsecase(FetchBrTitleInfoPort):
    """
    - fetch_br_title_info: Pnu 기준으로 외부 API 조회만 수행
    - fetch_and_save_by_house_platform: pnu_cd + house_platform_id를 받아
      외부 API 조회 후 dj_bldrgst에 저장하는 유즈케이스
    """

    def __init__(
        self,
        ledger_external_port: BuildingLedgerExternalPort,
        repository_port: BuildingLedgerRepositoryPort,
    ) -> None:
        self.ledger_external_port = ledger_external_port
        self.repository_port = repository_port

    def fetch_br_title_info(self, pnu: Pnu) -> Dict[str, Any]:
        # 외부 API 호출
        params = pnu.to_params()
        return self.ledger_external_port.get_br_title_info(**params)

    def fetch_and_save_by_house_platform(
        self,
        pnu_cd: str,
        house_platform_id: int,
    ) -> Dict[str, Any]:
        """
        1. pnu_cd → Pnu VO로 변환 후 외부 API 호출
        2. 응답 item 리스트 추출
        3. house_platform_id + pnu_cd 기준 기존 데이터 삭제 후 새로 저장
        """

        pnu = Pnu(pnu_cd)
        params = pnu.to_params()

        try:
            response = self.ledger_external_port.get_br_title_info(**params)
        except Exception as e:
            logger.error(
                "API call failed pnu_cd=%s, house_platform_id=%s, err=%s",
                pnu_cd,
                house_platform_id,
                e,
            )
            raise

        body = response.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        if not items:
            logger.warning(
                "zero items for pnu_cd=%s, house_platform_id=%s",
                pnu_cd,
                house_platform_id,
            )
            return response

        self.repository_port.replace_all_by_house_platform_id(
            house_platform_id=house_platform_id,
            pnu_cd=pnu_cd,
            items=items,
        )

        logger.info(
            "successfully saved %d item(s) for pnu_cd=%s, house_platform_id=%s",
            len(items),
            pnu_cd,
            house_platform_id,
        )

        return response