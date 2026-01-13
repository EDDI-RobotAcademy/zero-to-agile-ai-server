from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AppUser:
    user_id: Optional[int]
    name: str
    nickname: Optional[str]
    phone_number: Optional[str]
    email: str
    signup_type: str
    user_type: str
    university_name: Optional[str] = None
    is_deleted: bool = False
    first_create_dt: Optional[datetime] = None
    last_update_dt: Optional[datetime] = None

    # def mark_deleted(self):
    #     """유저를 삭제 상태로 변경하는 도메인 로직"""
    #     self.is_deleted = True

    def update_profile(self, name: Optional[str] = None, nickname: Optional[str] = None, phone_number: Optional[str] = None, university_name: Optional[str] = None):
        """유저의 기본 프로필 정보를 수정하는 도메인 로직"""
        if name:
            self.name = name
        if nickname:
            self.nickname = nickname
        if phone_number:
            self.phone_number = phone_number
        if university_name:
            self.university_name = university_name
