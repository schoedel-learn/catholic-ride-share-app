from enum import Enum
from typing import Dict

from fastapi import WebSocket


class WebSocketAction(str, Enum):
    NEW_REQUEST = "new_request"
    RIDE_ACCEPTED = "ride_accepted"
    RIDE_UPDATED = "ride_updated"


class ConnectionManager:
    def __init__(self):
        # Maps user_id to their active websocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast_to_users(self, message: dict, user_ids: list[int]):
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()
