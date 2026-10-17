from datetime import date, datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.enums import StatusEnum
from src.schemas.evaluation_schemas import EvaluationReadSchema
from src.schemas.user_schemas import UserRead


class CommentCreate(BaseModel):
    """
    Comment create schema.

    Attributes:
        text(str): The comment text.
        created_at(datetime) The date and the time of the comment creation.
    """

    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class CommentRead(CommentCreate):
    """
    Comment read schema.

    Attributes:
        user_id (UUID): The ID of the user, who has created the comment.

    """

    user_id: UUID


class TaskCreate(BaseModel):
    """
    Task create schema.

    Attributes:
        name (str): The name of the task.
        description (str): A description of the task.
        deadline (date): The deadline for the task.
        user_id (Optional[UUID]): The ID of the user assigned to
            the task, or None if not assigned.
    """

    name: str = Field(max_length=250)
    description: str
    deadline: date = Field(ge=date.today())
    user_id: UUID | None = None


class TaskModify(BaseModel):
    """
    Task modify schema.

    Attributes:
        name (Optional(str)): The name of the task.
        description (Optional(str)): A description of the task.
        deadline (Optional(date)): The deadline for the task.
        user_id (Optional[int]): The ID of the user assigned to
            the task, or None if not assigned.
    """

    name: str | None = Field(max_length=250, default=None)
    description: str | None = None
    deadline: date | None = Field(ge=date.today(), default=None)
    user_id: UUID | None = None


class TaskRead(BaseModel):
    """
    Task read schema.

    Attributes:
        id (UUID): The ID of the task.
        name (str): The name of the task.
        description (str): A description of the task.
        deadline (date): The deadline for the task.
        status (str): The current status of the task.
        comments (list[CommentRead]): The list of comments associated with this task.
        user (Optional(User)): The User object representing the executor
            of the task.
        evaluation (Optional(Evaluation)): The evaluation for the task.
    """

    id: UUID
    name: str
    description: str
    deadline: date
    status: str
    user: UserRead | None = None
    evaluation: EvaluationReadSchema | None = None
    comments: list["CommentRead"] | None = None


class TaskUpdate(BaseModel):
    """
    Task update schema.

    Attributes:
        status(StatusEnum) A status of the task. Сan take values "opened", "progress", "done".
            By default, is progress.

    """

    status: StatusEnum = Field(default=StatusEnum.PROGRESS)
