from sqlalchemy import String, func, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base
from datetime import datetime
import uuid


class ChatRoom(Base):
    """Model representing a chat room/space where users can exchange messages."""

    __tablename__ = 'chatrooms'  # Database table name

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Primary key, automatically generated UUID

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # Chat room name, must be unique and cannot be null

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
     # Timestamp of when the chat room was created, 
     # defaults to current time on database server


    # One-to-many relationship with Message model
    # Lists all messages belonging to this chat room
    messages: Mapped[list["Message"]] = relationship(back_populates="room") # pyright: ignore[reportUndefinedVariable]
    
