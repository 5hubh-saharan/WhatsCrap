from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.models.chatroom import ChatRoom
from app.models.message import Message
import uuid


async def get_all_rooms(db: AsyncSession) -> List[ChatRoom]:
    # Retrieve all chat rooms
    stmt = select(ChatRoom).order_by(ChatRoom.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_room(db: AsyncSession, room_id: str) -> ChatRoom | None:
    # Get specific chat room
    try:
        stmt = select(ChatRoom).where(ChatRoom.id == uuid.UUID(room_id))
        result = await db.execute(stmt)
        return result.scalars().first()
    except ValueError:
        return None


async def create_room_service(db: AsyncSession, name: str) -> ChatRoom:
    # Create a new chat room
    stmt = select(ChatRoom).where(ChatRoom.name == name)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=400, detail="Room name already exists")
    # Create and persist the new chat room

    room = ChatRoom(name=name)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_messages_for_room(db: AsyncSession, room_id: str) -> List[Message]:
    # Retrieve messages for a specific chat room
    try:
        # Build the query to get messages with user details
        stmt = (
            select(Message)
            .options(selectinload(Message.user))
            .where(Message.room_id == uuid.UUID(room_id))
            .order_by(Message.created_at)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except ValueError:
        return []


async def create_message(db: AsyncSession, room_id: str, user_id: str, content: str) -> Message:
    # Create a new message in a chat room
    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if len(content) > 1000:
        raise HTTPException(status_code=400, detail="Message too long")

    message = Message(
        content=content.strip(),
        user_id=uuid.UUID(user_id),
        room_id=uuid.UUID(room_id),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message