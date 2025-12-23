from sqlalchemy.orm import Session
from typing import Optional, Dict
from modules.abang_user.adapter.output.abang_user_model import AbangUser

class AbangUserRepository:
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
                "created_at": new_user.created_at,
                "updated_at": new_user.updated_at
            }
        finally:
            db.close()
