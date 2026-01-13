from modules.observations_assistance.application.port_out.building_ledger_repository_port import BuildingLedgerRepositoryPort
from infrastructure.orm.dj_bldrgst import DjBjdrgst


class DjBjdrgstRepositoryAdapter(BuildingLedgerRepositoryPort):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def replace_all_by_house_platform_id(
            self,
            house_platform_id: int,
            pnu_cd: str,
            items: list[dict],
    ) -> None:
        with self.session_factory() as session:
            try:
                # 1) 기존 row 삭제 (일단 삭제로 구현)
                session.query(DjBjdrgst).filter(
                    DjBjdrgst.house_platform_id == house_platform_id,
                    DjBjdrgst.pnu_cd == pnu_cd
                ).delete()

                # 2) item 개수만큼 insert (여러 동 나올 수도 있으니)
                for item in items:
                    row = DjBjdrgst(
                        house_platform_id=house_platform_id,
                        pnu_cd=pnu_cd,
                        mgm_bldrgst_pk=item.get("mgmBldrgstPk"),
                        rnum=item.get("rnum"),
                        plat_plc=item.get("platPlc"),
                        sigungu_cd=item.get("sigunguCd"),
                        bjdong_cd=item.get("bjdongCd"),
                        plat_gb_cd=item.get("platGbCd"),
                        bun=item.get("bun"),
                        ji=item.get("ji"),
                        regstr_gb_cd=item.get("regstrGbCd"),
                        regstr_gb_cd_nm=item.get("regstrGbCdNm"),
                        regstr_kind_cd=item.get("regstrKindCd"),
                        regstr_kind_cd_nm=item.get("regstrKindCdNm"),
                        new_plat_plc=item.get("newPlatPlc"),
                        bld_nm=item.get("bldNm"),
                        bylot_cnt=item.get("bylotCnt"),
                        na_road_cd=item.get("naRoadCd"),
                        na_bjdong_cd=item.get("naBjdongCd"),
                        na_ugrnd_cd=item.get("naUgrndCd"),
                        na_main_bun=item.get("naMainBun"),
                        na_sub_bun=item.get("naSubBun"),
                        dong_nm=item.get("dongNm"),
                        main_atch_gb_cd=item.get("mainAtchGbCd"),
                        main_atch_gb_cd_nm=item.get("mainAtchGbCdNm"),
                        plat_area=item.get("platArea"),
                        arch_area=item.get("archArea"),
                        bc_rat=item.get("bcRat"),
                        tot_area=item.get("totArea"),
                        vl_rat_estm_tot_area=item.get("vlRatEstmTotArea"),
                        vl_rat=item.get("vlRat"),
                        strct_cd=item.get("strctCd"),
                        strct_cd_nm=item.get("strctCdNm"),
                        etc_strct=item.get("etcStrct"),
                        main_purps_cd=item.get("mainPurpsCd"),
                        main_purps_cd_nm=item.get("mainPurpsCdNm"),
                        etc_purps=item.get("etcPurps"),
                        roof_cd=item.get("roofCd"),
                        roof_cd_nm=item.get("roofCdNm"),
                        etc_roof=item.get("etcRoof"),
                        hhld_cnt=item.get("hhldCnt"),
                        fmly_cnt=item.get("fmlyCnt"),
                        heit=item.get("heit"),
                        grnd_flr_cnt=item.get("grndFlrCnt"),
                        ugrnd_flr_cnt=item.get("ugrndFlrCnt"),
                        ride_use_elvt_cnt=item.get("rideUseElvtCnt"),
                        emgen_use_elvt_cnt=item.get("emgenUseElvtCnt"),
                        atch_bld_cnt=item.get("atchBldCnt"),
                        atch_bld_area=item.get("atchBldArea"),
                        tot_dong_tot_area=item.get("totDongTotArea"),
                        indr_mech_utcnt=item.get("indrMechUtcnt"),
                        indr_mech_area=item.get("indrMechArea"),
                        oudr_mech_utcnt=item.get("oudrMechUtcnt"),
                        oudr_mech_area=item.get("oudrMechArea"),
                        indr_auto_utcnt=item.get("indrAutoUtcnt"),
                        indr_auto_area=item.get("indrAutoArea"),
                        oudr_auto_utcnt=item.get("oudrAutoUtcnt"),
                        oudr_auto_area=item.get("oudrAutoArea"),
                        pms_day=item.get("pmsDay"),
                        stcns_day=item.get("stcnsDay"),
                        use_apr_day=item.get("useAprDay"),
                        pmsno_year=item.get("pmsnoYear"),
                        pmsno_kik_cd=item.get("pmsnoKikCd"),
                        pmsno_kik_cd_nm=item.get("pmsnoKikCdNm"),
                        pmsno_gb_cd=item.get("pmsnoGbCd"),
                        pmsno_gb_cd_nm=item.get("pmsnoGbCdNm"),
                        ho_cnt=item.get("hoCnt"),
                        engr_grade=item.get("engrGrade"),
                        engr_rat=item.get("engrRat"),
                        engr_epi=item.get("engrEpi"),
                        gn_bld_grade=item.get("gnBldGrade"),
                        gn_bld_cert=item.get("gnBldCert"),
                        itg_bld_grade=item.get("itgBldGrade"),
                        itg_bld_cert=item.get("itgBldCert"),
                        crtn_day=item.get("crtnDay"),
                        rserthqk_dsgn_apply_yn=item.get("rserthqkDsgnApplyYn"),
                        rserthqk_ablty=item.get("rserthqkAblty"),
                    )
                    session.add(row)

                session.commit()

            except Exception as e:
                session.rollback()
                print(f"[ERROR] DB save failed pnu_cd={pnu_cd}, house_platform_id={house_platform_id}, err={e}")