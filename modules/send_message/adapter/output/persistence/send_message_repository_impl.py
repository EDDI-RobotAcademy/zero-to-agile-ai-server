from typing import List, Optional
from sqlalchemy.orm import Session
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.send_message.domain.send_message import SendMessage
from modules.send_message.infrastructure.orm.send_message_orm import SendMessageORM

class SendMessageRepositoryImpl(SendMessageRepository):
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def _to_domain(self, orm: SendMessageORM) -> SendMessage:
        return SendMessage(
            send_message_id=orm.send_message_id,
            house_platform_id=orm.house_platform_id,
            finder_request_id=orm.finder_request_id,
            accept_type=orm.accept_type,
            message=orm.message,
            receiver_id=orm.receiver_id,
            sender_id=orm.sender_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    def save(self, send_message: SendMessage) -> SendMessage:
        db: Session = self.db_session_factory()
        try:
            if send_message.send_message_id:
                orm = db.query(SendMessageORM).filter(SendMessageORM.send_message_id == send_message.send_message_id).first()
                if orm:
                    orm.accept_type = send_message.accept_type
                    orm.message = send_message.message
                    # Typically other fields like IDs don't change, but if needed:
                    # orm.house_platform_id = send_message.house_platform_id
                    db.commit()
                    db.refresh(orm)
                    return self._to_domain(orm)
            
            # Create
            orm = SendMessageORM(
                house_platform_id=send_message.house_platform_id,
                finder_request_id=send_message.finder_request_id,
                accept_type=send_message.accept_type,
                message=send_message.message,
                receiver_id=send_message.receiver_id,
                sender_id=send_message.sender_id
            )
            db.add(orm)
            db.commit()
            db.refresh(orm)
            return self._to_domain(orm)
        finally:
            db.close()

    def find_by_id(self, send_message_id: int) -> Optional[SendMessage]:
        db: Session = self.db_session_factory()
        try:
            orm = db.query(SendMessageORM).filter(SendMessageORM.send_message_id == send_message_id).first()
            if orm:
                return self._to_domain(orm)
            return None
        finally:
            db.close()

    def find_by_sender_id(self, sender_id: int) -> List[SendMessage]:
        db: Session = self.db_session_factory()
        try:
            orms = db.query(SendMessageORM).filter(SendMessageORM.sender_id == sender_id).all()
            return [self._to_domain(orm) for orm in orms]
        finally:
            db.close()

    def find_by_receiver_id(self, receiver_id: int) -> List[SendMessage]:
        db: Session = self.db_session_factory()
        try:
            orms = (
                db.query(SendMessageORM)
                .filter(
                    SendMessageORM.receiver_id == receiver_id,
                    SendMessageORM.accept_type != 'D'  # D 제외
                ).all())
            return [self._to_domain(orm) for orm in orms]
        finally:
            db.close()

    def find_by_house_and_request(self, house_platform_id: int, finder_request_id: int) -> Optional[SendMessage]:
        db: Session = self.db_session_factory()
        try:
            orm = db.query(SendMessageORM).filter(
                SendMessageORM.house_platform_id == house_platform_id,
                SendMessageORM.finder_request_id == finder_request_id
            ).first()
            if orm:
                return self._to_domain(orm)
            return None
        finally:
            db.close()

    def find_accepted_by_receiver_id(self, receiver_id: int) -> List[SendMessage]:
        db: Session = self.db_session_factory()
        try:
            orms = db.query(SendMessageORM).filter(
                SendMessageORM.receiver_id == receiver_id,
                SendMessageORM.accept_type == 'Y'
            ).all()
            return [self._to_domain(orm) for orm in orms]
        finally:
            db.close()

