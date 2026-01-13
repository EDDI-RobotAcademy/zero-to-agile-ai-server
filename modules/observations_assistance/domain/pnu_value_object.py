class Pnu:
    def __init__(self, pnu: str):
        if len(pnu) != 19 or not pnu.isdigit():
            raise ValueError("PNU must be exactly 19 numeric characters")

        self.sigungu_cd = pnu[0:5]
        self.bjdong_cd = pnu[5:10]
        self.plat_gb_cd = 0 # 일괄 대지로 박아둠. 디비에서 변경 없이..
        self.bun = pnu[11:15]
        self.ji = pnu[15:19]

    def to_params(self) -> dict:
        return {
            "sigunguCd": self.sigungu_cd,
            "bjdongCd": self.bjdong_cd,
            "platGbCd": self.plat_gb_cd,
            "bun": self.bun,
            "ji": self.ji,
        }