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
    WebSocket聊天端点
    
    参数顺序：
    1. websocket: WebSocket对象（无默认值）
    2. room_id: 房间ID（无默认值）
    3. db: 数据库会话（有默认值，使用Depends）
    """
    # 获取用户ID
    user_id = websocket.query_params.get("user_id")
    
    if not user_id:
        await websocket.close(code=1008)
        return

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        await websocket.close(code=1008)
        return

    # 验证用户
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        await websocket.close(code=1008)
        return

    # 连接管理器
    await manager.connect(room_id, websocket)
    
    # 发送欢迎消息给该用户
    await manager.send_personal_json(websocket, {
        "type": "system",
        "message": f"Welcome to the chat, {user.username}!",
        "timestamp": datetime.now().isoformat()
    })
    
    # 通知其他用户有人加入
    await manager.broadcast_json(room_id, {
        "type": "system",
        "message": f"{user.username} has joined the chat",
        "timestamp": datetime.now().isoformat()
    }, exclude_websocket=websocket)

    try:
        while True:
            data = await websocket.receive_text()
            
            # 更新活跃时间
            manager.update_activity(websocket)
            
            # 处理心跳消息
            if data == "PING":
                await websocket.send_text("PONG")
                continue
            
            # 跳过系统消息格式
            if data.startswith("[System]") or data.startswith("{"):
                continue
            
            # 创建消息记录
            msg = await create_message(db, room_id, user_id, data)

            # 广播给所有用户
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
        
        # 通知其他用户有人离开
        await manager.broadcast_json(room_id, {
            "type": "system",
            "message": f"{user.username} has left the chat",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        manager.disconnect(room_id, websocket)
        await websocket.close(code=1011)