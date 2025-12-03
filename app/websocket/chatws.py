import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.websocket.manager import manager
from app.services.chat_service import create_message
from app.models.user import User

router = APIRouter()


@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    db: AsyncSession = Depends(get_db),
):
    # For now, we pass user_id via query param from the frontend:
    # ws://.../ws/chat/{room_id}?user_id=<uuid>
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=1008)
        return

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        await websocket.close(code=1008)
        return

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            msg = await create_message(db, room_id, user_id, data)

            payload = json.dumps(
                {
                    "room_id": room_id,
                    "user_id": str(user.id),
                    "username": user.username,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
            )

            await manager.broadcast(room_id, payload)

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    except Exception:
        manager.disconnect(room_id, websocket)
        await websocket.close(code=1011)
