from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, func
from infrastructure.db.postgres import Base

class SendMessageORM(Base):
    __tablename__ = "send_message"

    send_message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    house_platform_id = Column(BigInteger, nullable=False) # FK to house_platform logically
    finder_request_id = Column(BigInteger, ForeignKey("finder_request.finder_request_id"), nullable=False)
    accept_type = Column(String(1), default='W', nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    receiver_id = Column(BigInteger, nullable=False)
    sender_id = Column(BigInteger, nullable=False)
