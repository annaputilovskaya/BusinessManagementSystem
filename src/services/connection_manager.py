from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    Registry of active WebSocket connections grouped by task room.
    """

    def __init__(self) -> None:
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    def connect(self, task_id: UUID, user_id: UUID, websocket: WebSocket) -> None:
        """Register a websocket in the task room."""
        self.active_connections.setdefault(task_id, {})[user_id] = websocket

    def disconnect(self, task_id: UUID, user_id: UUID) -> None:
        """Remove a websocket from the task room, dropping empty rooms."""
        room = self.active_connections.get(task_id)
        if room is None:
            return
        room.pop(user_id, None)
        if not room:
            self.active_connections.pop(task_id, None)

    async def broadcast(self, task_id: UUID, payload: dict) -> None:
        """Send payload to every websocket in the given task room only."""
        for websocket in list(self.active_connections.get(task_id, {}).values()):
            try:
                await websocket.send_json(payload)
            except (WebSocketDisconnect, RuntimeError):
                # dead socket — skip, will be cleaned up on disconnect
                pass


manager = ConnectionManager()
