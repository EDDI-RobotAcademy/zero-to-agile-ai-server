from typing import List, Dict, Any

from sqlalchemy import text

from modules.observations_assistance.application.port_out.building_ledger_repository_port import BuildingLedgerRepositoryPort
from infrastructure.db.postgres import get_db_session
from sqlalchemy.orm import Session
from infrastructure.orm.dj_bldrgst import DjBjdrgst


# API 응답 key → db 컬럼명 매핑
COLUMN_MAP: Dict[str, str] = {
    "rnum": "rnum",
    "platPlc": "plat_plc",
    "sigunguCd": "sigungu_cd",
    "bjdongCd": "bjdong_cd",
    "platGbCd": "plat_gb_cd",
    "bun": "bun",
    "ji": "ji",
    "mgmBldrgstPk": "mgm_bldrgst_pk",
    "regstrGbCd": "regstr_gb_cd",
    "regstrGbCdNm": "regstr_gb_cd_nm",
    "regstrKindCd": "regstr_kind_cd",
    "regstrKindCdNm": "regstr_kind_cd_nm",
    "newPlatPlc": "new_plat_plc",
    "bldNm": "bld_nm",
    "bylotCnt": "bylot_cnt",
    "naRoadCd": "na_road_cd",
    "naBjdongCd": "na_bjdong_cd",
    "naUgrndCd": "na_ugrnd_cd",
    "naMainBun": "na_main_bun",
    "naSubBun": "na_sub_bun",
    "dongNm": "dong_nm",
    "mainAtchGbCd": "main_atch_gb_cd",
    "mainAtchGbCdNm": "main_atch_gb_cd_nm",
    "platArea": "plat_area",
    "archArea": "arch_area",
    "bcRat": "bc_rat",
    "totArea": "tot_area",
    "vlRatEstmTotArea": "vl_rat_estm_tot_area",
    "vlRat": "vl_rat",
    "strctCd": "strct_cd",
    "strctCdNm": "strct_cd_nm",
    "etcStrct": "etc_strct",
    "mainPurpsCd": "main_purps_cd",
    "mainPurpsCdNm": "main_purps_cd_nm",
    "etcPurps": "etc_purps",
    "roofCd": "roof_cd",
    "roofCdNm": "roof_cd_nm",
    "etcRoof": "etc_roof",
    "hhldCnt": "hhld_cnt",
    "fmlyCnt": "fmly_cnt",
    "heit": "heit",
    "grndFlrCnt": "grnd_flr_cnt",
    "ugrndFlrCnt": "ugrnd_flr_cnt",
    "rideUseElvtCnt": "ride_use_elvt_cnt",
    "emgenUseElvtCnt": "emgen_use_elvt_cnt",
    "atchBldCnt": "atch_bld_cnt",
    "atchBldArea": "atch_bld_area",
    "totDongTotArea": "tot_dong_tot_area",
    "indrMechUtcnt": "indr_mech_utcnt",
    "indrMechArea": "indr_mech_area",
    "oudrMechUtcnt": "oudr_mech_utcnt",
    "oudrMechArea": "oudr_mech_area",
    "indrAutoUtcnt": "indr_auto_utcnt",
    "indrAutoArea": "indr_auto_area",
    "oudrAutoUtcnt": "oudr_auto_utcnt",
    "oudrAutoArea": "oudr_auto_area",
    "pmsDay": "pms_day",
    "stcnsDay": "stcns_day",
    "useAprDay": "use_apr_day",
    "pmsnoYear": "pmsno_year",
    "pmsnoKikCd": "pmsno_kik_cd",
    "pmsnoKikCdNm": "pmsno_kik_cd_nm",
    "pmsnoGbCd": "pmsno_gb_cd",
    "pmsnoGbCdNm": "pmsno_gb_cd_nm",
    "hoCnt": "ho_cnt",
    "engrGrade": "engr_grade",
    "engrRat": "engr_rat",
    "engrEpi": "engr_epi",
    "gnBldGrade": "gn_bld_grade",
    "gnBldCert": "gn_bld_cert",
    "itgBldGrade": "itg_bld_grade",
    "itgBldCert": "itg_bld_cert",
    "crtnDay": "crtn_day",
    "rserthqkDsgnApplyYn": "rserthqk_dsgn_apply_yn",
    "rserthqkAblty": "rserthqk_ablty",
}


class DjBjdrgstRepository(BuildingLedgerRepositoryPort):
    """
    dj_bldrgst 테이블에 직접 SQL로 접근하는 Adapter.
    - 기존 row 삭제
    - 새로운 item 전체 insert
    """

    def __init__(self, session: Session):
        self.session = session

    def delete_by_hp_id(self, house_platform_id: int):
        self.session.query(DjBjdrgst).filter(
            DjBjdrgst.house_platform_id == house_platform_id
        ).delete()

    def bulk_insert(self, items: list[DjBjdrgst]):
        self.session.add_all(items)
        self.session.commit()

    def replace_all_by_house_platform_id(
        self,
        house_platform_id: int,
        pnu_cd: str,
        items: List[Dict[str, Any]],
    ) -> None:
        session = next(get_db_session())

        try:
            # 1) 기존 데이터 삭제
            session.execute(
                text(
                    """
                    DELETE FROM dj_bldrgst
                    WHERE house_platform_id = :hid
                      AND pnu_cd = :pnu
                    """
                ),
                {"hid": house_platform_id, "pnu": pnu_cd},
            )

            # 2) 새 데이터 insert
            for item in items:
                params: Dict[str, Any] = {
                    "house_platform_id": house_platform_id,
                    "pnu_cd": pnu_cd,
                }

                for api_key, col_name in COLUMN_MAP.items():
                    params[col_name] = item.get(api_key)

                columns = ", ".join(params.keys())
                placeholders = ", ".join(f":{k}" for k in params.keys())

                sql = text(
                    f"""
                    INSERT INTO dj_bldrgst ({columns})
                    VALUES ({placeholders})
                    """
                )

                session.execute(sql, params)

            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()