from sqlalchemy import Column, TIMESTAMP, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class ChatRoom(Base):
    __tablename__ = 'chatrooms'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    messages = relationship("Message", back_populates="room")
