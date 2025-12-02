from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chatroom import ChatRoom
from app.models.message import Message
import uuid



async def get_all_rooms(self, db: AsyncSession):
    statement = select(ChatRoom).order_by(ChatRoom.created_at)
    result = await db.execute(statement)
    return result.scalars().all()

async def get_room(self, db: AsyncSession, room_id: str):
    statement = select(ChatRoom).where(ChatRoom.id == uuid.UUID(room_id))
    result = await db.execute(statement)
    return result.scalars.first()

async def create_room(self, db: AsyncSession, name: str):
    room = ChatRoom(name=name)
    db.add(room)
    await db.commit()
    await db.refresh()
    return room
    