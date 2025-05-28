from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.evaluation_schemas import EvaluationReadSchema
from src.schemas.user_schemas import UserRead


class CommentCreate(BaseModel):
    """
    Comment create schema.

    Attributes:
        text(str): The comment text.
    """

    text: str


class CommentRead(CommentCreate):
    """
    Comment read schema.

    Attributes:
        created_at(datetime) The date and the time of the comment creation.
        user_id (int): The ID of the user, who has created the comment.

    """
    created_at: datetime
    user_id: int


class TaskCreate(BaseModel):
    """
    Task create schema.

    Attributes:
        name (str): The name of the task.
        description (str): A description of the task.
        deadline (date): The deadline for the task.
        user_id (Optional[int]): The ID of the user assigned to
            the task, or None if not assigned.
    """
    name: str = Field(max_length=250)
    description: str
    deadline: date = Field(ge=date.today())
    user_id: int | None = None


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
    user_id: int | None = None



class TaskRead(BaseModel):
    """
    Task read schema.

    Attributes:
        id (int): The ID of the task.
        name (str): The name of the task.
        description (str): A description of the task.
        deadline (date): The deadline for the task.
        status (str): The current status of the task.
        comments (list[CommentRead]): The list of comments associated with this task.         a relationship.
        executor (Optional(User)): The User object representing the executor
            of the task.
        evaluation (Optional(Evaluation)): The evaluation for the task.
    """
    id: int
    name: str
    description: str
    deadline: date
    status: str
    executor: UserRead | None = None
    evaluation: EvaluationReadSchema | None = None
    comments: list["CommentRead"] | None = None


class TaskUpdate(BaseModel):
    """
    Task update schema.

    Attributes:
        status(Literal) A status of the task. Сan take values "opened", "progress", "done".
            By default, is progress.

    """
    status: Literal["opened", "progress", "done"] = Field(default="progress")
