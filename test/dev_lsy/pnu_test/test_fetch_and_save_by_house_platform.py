from modules.observations_assistance.application.usecase.fetch_br_title_info_usecase import FetchBrTitleInfoUsecase
from modules.observations_assistance.adapter.output.building_ledger_external_client import BuildingLedgerExternalClient
from modules.observations_assistance.adapter.output.repository.dj_bjdrgst_repository import DjBjdrgstRepository


def test_fetch_and_save_by_house_platform():
    pnu_cd = "1141011200101010011"
    house_platform_id = 285

    external_client = BuildingLedgerExternalClient()
    repository = DjBjdrgstRepository()

    usecase = FetchBrTitleInfoUsecase(
        ledger_external_port=external_client,
        repository_port=repository,
    )

    # --- when ---
    response = usecase.fetch_and_save_by_house_platform(
        pnu_cd=pnu_cd,
        house_platform_id=house_platform_id,
    )

    print(f"API Response: {response}")