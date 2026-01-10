from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class DistanceFeatureObservation:
    university_id: int
    학교까지_분: float
    거리_백분위: float
    거리_버킷: str
    거리_비선형_점수: float
    calculated_at: datetime = datetime.now(timezone.utc)
