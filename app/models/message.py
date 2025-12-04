from sqlalchemy import String, func, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base
from datetime import datetime
import uuid


class Message(Base):
    """Model representing an individual message sent in a chat room."""

    __tablename__ = 'messages'# Database table name

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Primary key, automatically generated UUID

    content: Mapped[str] = mapped_column(String)
    # Content/text of the message

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now())
     # Timestamp of when the message was created

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'))
     # Foreign key to the user who sent this message

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('chatrooms.id'))
     # Foreign key to the chat room where this message was sent

    user: Mapped["User"] = relationship(back_populates="messages") # pyright: ignore[reportUndefinedVariable]
    room: Mapped["ChatRoom"] = relationship(back_populates="messages") # pyright: ignore[reportUndefinedVariable]
