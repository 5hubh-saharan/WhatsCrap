from sqlalchemy import Column, TIMESTAMP, TEXT, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True)
    content = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    room_id = Column(UUID(as_uuid=True), ForeignKey('chatrooms.id'))

    user = relationship("User", back_populates="messages")
    room = relationship("ChatRoom", back_populates="messages")
