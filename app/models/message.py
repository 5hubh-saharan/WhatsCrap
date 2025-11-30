from sqlalchemy import String, func, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base
from datetime import datetime
import uuid


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('chatrooms.id'))

    user: Mapped["User"] = relationship(back_populates="messages")
    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
