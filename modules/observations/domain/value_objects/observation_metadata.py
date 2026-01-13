from dataclasses import dataclass


@dataclass(frozen=True)
class ObservationMetadata:
    관측치_버전: str
    원본_데이터_버전: str

    def __post_init__(self):
        if not self.관측치_버전:
            raise ValueError("관측치 버전은 비어 있을 수 없습니다.")

        if not self.원본_데이터_버전:
            raise ValueError("원본 데이터 버전은 비어 있을 수 없습니다.")

    @classmethod
    def from_raw(cls, raw_house, observation_version: str = "v1"):
        # if not hasattr(raw_house, "data_version"):
            # TODO: 원본 데이터 버전 관리 필요
            # raise ValueError("Raw House 객체에 'data_version' 속성이 존재하지 않습니다.")
        raw_house_version = "v1"  # raw_house.data_version

        return cls(
            관측치_버전=observation_version,
            원본_데이터_버전=raw_house_version
        )
