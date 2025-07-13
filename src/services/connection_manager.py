from uuid import UUID

from fastapi import WebSocket, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Comment
from src.schemas.task_schemas import CommentCreate
from src.services.dependencies import get_team_task_by_id
from src.services.task_services import add_comment


class ConnectionManager:
    """
    Class for working with web socket connections.
    """

    def __init__(self):
        """
        Initialize connection manager.
        """

        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(
            self, websocket: WebSocket, task_id: UUID, session: AsyncSession, user: User
    ) -> list[Comment | None] | None:
        """
        Establishes a connection with the user.

        Confirms connection and returns the list of task comments if comments exist.

        Args:
            websocket(WebSocket): The two-way communication with the server.
            task_id(UUID): The UUID of the task, which is commented.
            session (AsyncSession): The asynchronous session to interact with the database.
            user (User): The user who is joined to comment the task.
        """

        await websocket.accept()
        task = await get_team_task_by_id(task_id, session, user)
        if not task:
            await websocket.close(code=1008, reason="No task found.")
        else:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = {}
            self.active_connections[task_id][user.id] = websocket
            return task.comments

    async def send_comments_history(self, websocket: WebSocket, comments: list[Comment] | None):
        """
        Sends the history of task comments for the connected user.

        Args:
            websocket(WebSocket): The two-way communication with the server.
            comments(list[Comment]): The list of the task comments.
        """

        if comments:
            for comment in comments:
                await websocket.send_text(
                    f"{comment.user_id} at {comment.created_at} added comment: \"{comment.text}\""
                )

    async def disconnect(self, task_id: UUID, user: User):
        """
        Closes the connection and removes it from the list of active connections.

        Args:
            task_id(UUID): The UUID of the task, which was commented.
            user (User): The user who was joined to comment the task.
        """

        if task_id in self.active_connections and user.id in self.active_connections[task_id]:
            del self.active_connections[task_id][user.id]
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast(
            self, data:str, task_id: UUID, session: AsyncSession, user: User, background_tasks: BackgroundTasks
    ) -> None:
        """
        Sends the comment to all users subscribed to the task and save it to the database.

        Args:
            data(str): The comment text entered by the user.
            task_id(UUID): The UUID of the task, which is commented.
            session (AsyncSession): The asynchronous session to interact with the database.
            user (User): The user who is joined to comment the task.
            background_tasks(BackgroundTasks): FastAPI background tasks.
        """

        comment_in = CommentCreate(text=data)
        background_tasks.add_task(add_comment, comment_in, task_id, session, user)
        for task_id in self.active_connections:
            for user_id, websocket in self.active_connections[task_id].items():
                await websocket.send_text(
                    f"{user.id} at {comment_in.created_at} added comment: \"{comment_in.text}\""
                )


manager = ConnectionManager()
