from datetime import date, datetime
from typing import Literal

from sqlalchemy import ForeignKey, Enum, DateTime, text as sqla_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.evaluation import Evaluation

StatusEnum = Literal["opened", "progress", "done"]


class Comment(Base):
    """
    Comment model.

    Attributes:
        text (str): The comment text.
        created_at (datetime): The date and the time of the comment creation.
        task_id (int): The ID of the task assigned to the comment.
        user_id (int): The ID of the user, who has created the comment.
        task (Task): The Task object associated with this comment, linked via
            a relationship.
    """

    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sqla_text("timezone('utc', now())"),
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    task: Mapped["Task"] = relationship("Task", back_populates="comments")

    def __str__(self):
        """
        Returns the string representation of the comment object.
        """
        return f"{self.id}"


class Task(Base):
    """
    Task model.

    Attributes:
        name (str): The name of the task.
        description (str): A description of the task.
        deadline (date): The deadline for the task.
        status (StatusEnum): The current status of the task,
            defaults to opened.
        team_id (int): The ID of the team assigned to the task.
        user_id (Optional[int]): The ID of the user assigned to
            the task, or None if not assigned.
        comments (list[Comment]): The list of comments associated with this task, linked via
            a relationship.
        executor (User): The User object representing the executor
            of the task, establishing a relationship back to the User model.
        evaluation (Evaluation): The evaluation for the task,
            establishing a relationship back to the Evaluation model.
    """

    name: Mapped[str]
    description: Mapped[str]
    deadline: Mapped[date]
    status: Mapped[StatusEnum] = mapped_column(
        Enum("opened", "progress", "done", native_enum=False), default="opened"
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, default=None
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="task", lazy="selectin"
    )
    executor: Mapped["User"] = relationship(
        "User", back_populates="tasks", lazy="selectin"
    )
    evaluation: Mapped["Evaluation"] = relationship(
        "Evaluation", back_populates="task", lazy="selectin"
    )

    def __str__(self):
        """
        Returns the string representation of the task object.
        """
        return f"{self.id}. {self.name} ({self.team_id})"
