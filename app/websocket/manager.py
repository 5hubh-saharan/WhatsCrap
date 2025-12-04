from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_info: Dict[WebSocket, dict] = {}

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        
        self.connection_info[websocket] = {
            'room_id': room_id,
            'connected_at': datetime.now(),
            'last_active': datetime.now(),
        }

        print(f"User connected to room {room_id}")

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        room_conns = self.active_connections.get(room_id)
        if room_conns:
            room_conns.discard(websocket)
            if not room_conns:
                del self.active_connections[room_id]
        
        if websocket in self.connection_info:
            del self.connection_info[websocket]

        print(f"User disconnected from room {room_id}")

    async def send_personal_message(self, websocket: WebSocket, message: str) -> None:
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Failed to send personal message: {e}")

    async def send_personal_json(self, websocket: WebSocket, data: dict) -> None:
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Failed to send personal JSON: {e}")

    async def broadcast(self, room_id: str, message: str, exclude_websocket: WebSocket = None) -> None:
        """广播消息，可以排除某个连接"""
        connections = list(self.active_connections.get(room_id, set()))
        
        for connection in connections:
            if exclude_websocket and connection == exclude_websocket:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(room_id, connection)

    async def broadcast_json(self, room_id: str, data: dict, exclude_websocket: WebSocket = None) -> None:
        """广播JSON数据，可以排除某个连接"""
        connections = list(self.active_connections.get(room_id, set()))
        
        for connection in connections:
            if exclude_websocket and connection == exclude_websocket:
                continue
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(room_id, connection)

    def update_activity(self, websocket: WebSocket):
        if websocket in self.connection_info:
            self.connection_info[websocket]['last_active'] = datetime.now()


manager = ConnectionManager()