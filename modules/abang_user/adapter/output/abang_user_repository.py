from sqlalchemy.orm import Session
from typing import Optional, Dict
from modules.abang_user.adapter.output.abang_user_model import AbangUser
from modules.abang_user.domain.app_user import AppUser
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort

class AbangUserRepository(AbangUserRepositoryPort):
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def find_by_email(self, email: str) -> Optional[Dict]:
        db: Session = self.db_session_factory()
        try:
            user: Optional[AbangUser] = db.query(AbangUser).filter(
                AbangUser.email == email
            ).first()
            
            if not user:
                return None
            
            return {
                "abang_user_id": user.abang_user_id,
                "nickname": user.nickname,
                "email": user.email,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        finally:
            db.close()

    def create_user(self, nickname: str | None, email: str, user_type: str) -> Dict:
        db: Session = self.db_session_factory()
        try:
            new_user = AbangUser(
                nickname=nickname,
                email=email,
                user_type=user_type
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {
                "abang_user_id": new_user.abang_user_id,
                "nickname": new_user.nickname,
                "email": new_user.email,
                "user_type": new_user.user_type,
                "phone_number": new_user.phone_number,
                "created_at": new_user.created_at,
                "updated_at": new_user.updated_at
            }
        finally:
            db.close()

    def find_by_id(self, user_id: int) -> Optional[AppUser]:
        db: Session = self.db_session_factory()
        try:
            user: Optional[AbangUser] = db.query(AbangUser).filter(
                AbangUser.abang_user_id == user_id
            ).first()
            
            if not user:
                return None
            
            return AppUser(
                user_id=user.abang_user_id,
                name="", # DB에 name 컬럼이 없음, 로직에 따라 처리 필요
                nickname=user.nickname,
                phone_number=user.phone_number,
                email=user.email,
                signup_type="GOOGLE", # 임시, DB에 없음
                user_type=user.user_type,
                first_create_dt=user.created_at,
                last_update_dt=user.updated_at
            )
        finally:
            db.close()