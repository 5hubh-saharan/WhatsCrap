from sqlalchemy import String, func, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base
from datetime import datetime
import uuid

class User(Base):
    """Model representing a user in the chat application."""

    __tablename__ = 'users'# Database table name

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        # Primary key, automatically generated UUID

    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
        # Username, must be unique and cannot be null

    password: Mapped[str] = mapped_column(
        String, nullable=False)
        # Hashed password, cannot be null

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now())
        # Timestamp of when the user was created,


    # One-to-many relationship with Message model
    # Lists all messages sent by this user
    messages: Mapped[list["Message"]] = relationship(back_populates="user") # pyright: ignore[reportUndefinedVariable]
