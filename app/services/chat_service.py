from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.chatroom import ChatRoom
from app.models.message import Message
import uuid


async def get_all_rooms(db: AsyncSession):
    stmt = select(ChatRoom).order_by(ChatRoom.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_room(db: AsyncSession, room_id: str):
    stmt = select(ChatRoom).where(ChatRoom.id == uuid.UUID(room_id))
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_room_service(db: AsyncSession, name: str):
    stmt = select(ChatRoom).where(ChatRoom.name == name)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(status_code=400, detail="Room name already exists")

    room = ChatRoom(name=name)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_messages_for_room(db: AsyncSession, room_id: str):
    stmt = (
        select(Message)
        .options(selectinload(Message.user))
        .where(Message.room_id == uuid.UUID(room_id))
        .order_by(Message.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_message(db: AsyncSession, room_id: str, user_id: str, content: str):
    message = Message(
        content=content,
        user_id=uuid.UUID(user_id),
        room_id=uuid.UUID(room_id),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
