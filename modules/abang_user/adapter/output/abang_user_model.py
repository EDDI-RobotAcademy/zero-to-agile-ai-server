from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from infrastructure.db.postgres import Base

class AbangUser(Base):
    __tablename__ = "abang_user"

    abang_user_id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(255), nullable=True)
    phone_number = Column(String(11), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    user_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
