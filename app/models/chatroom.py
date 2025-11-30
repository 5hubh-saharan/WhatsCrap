from sqlalchemy import String, func, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base
from datetime import datetime
import uuid


class ChatRoom(Base):
    __tablename__ = 'chatrooms'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    messages: Mapped[list["Message"]] = relationship(back_populates="room")
