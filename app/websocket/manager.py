from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        room_conns = self.active_connections.get(room_id)
        if room_conns:
            room_conns.discard(websocket)
            if not room_conns:
                del self.active_connections[room_id]

    async def send_personal_message(self, websocket: WebSocket, message: str) -> None:
        await websocket.send_text(message)

    async def broadcast(self, room_id: str, message: str) -> None:
        for connection in self.active_connections.get(room_id, set()):
            await connection.send_text(message)


manager = ConnectionManager()
