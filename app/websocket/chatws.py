import json
import uuid
from datetime import datetime
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.websocket.manager import manager
from app.services.chat_service import create_message
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket Chat Endpoint

    Parameter Order:

    1. websocket: WebSocket object (no default value)

    2. room_id: Room ID (no default value)

    3. db: Database session (has a default value, use Depends)
    """
    # Get user ID
    user_id = websocket.query_params.get("user_id")
    
    if not user_id:
        await websocket.close(code=1008)
        return

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        await websocket.close(code=1008)
        return

    # Validate user
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        await websocket.close(code=1008)
        return

    # Connection manager
    await manager.connect(room_id, websocket)
    
    # Send a welcome message to the connected user
    await manager.send_personal_json(websocket, {
        "type": "system",
        "message": f"Welcome to the chat, {user.username}!",
        "timestamp": datetime.now().isoformat()
    })
    
    # Notify other users that someone has joined
    await manager.broadcast_json(room_id, {
        "type": "system",
        "message": f"{user.username} has joined the chat",
        "timestamp": datetime.now().isoformat()
    }, exclude_websocket=websocket)

    try:
        while True:
            data = await websocket.receive_text()
            
            # Update last active timestamp
            manager.update_activity(websocket)
            
            # Handle heartbeat messages
            if data == "PING":
                await websocket.send_text("PONG")
                continue
            
            # Skip system message formats
            if data.startswith("[System]") or data.startswith("{"):
                continue
            
            # Create a message record
            msg = await create_message(db, room_id, user_id, data)

            # Broadcast to all users
            broadcast_data = {
                "type": "message",
                "user_id": str(user.id),
                "username": user.username,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            
            await manager.broadcast_json(room_id, broadcast_data)

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        
        # Notify other users that someone has left
        await manager.broadcast_json(room_id, {
            "type": "system",
            "message": f"{user.username} has left the chat",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        manager.disconnect(room_id, websocket)
        await websocket.close(code=1011)