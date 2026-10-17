from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_date

from src.models import Base

if TYPE_CHECKING:
    from src.models.task import Task


class Evaluation(Base):
    """Evaluation model representing the assessment of tasks.

    Attributes:
        number (SmallInteger): The evaluation score.
        task_id (UUID): The identifier for the associated task.
        created_at (date): The date of evaluation creation.
        task (Task): The task associated with this evaluation,
            establishing a relationship back to the Task model.
    """

    __table_args__ = (
        CheckConstraint("number >= 1 AND number <= 5", name="check_number_range"),
    )

    number: Mapped[int]
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True, unique=True
    )
    created_at: Mapped[date] = mapped_column(
        Date,
        server_default=current_date(),
    )
    task: Mapped["Task"] = relationship("Task", back_populates="evaluation")

    def __str__(self):
        """
        Returns the string representation of the evaluation object.
        """

        return f"{self.task_id}: {self.number}"
