from datetime import date
from typing import Any

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_date

from src.models import Base


class Evaluation(Base):
    """Evaluation model representing the assessment of tasks.

    Attributes:
        number (SmallInteger): The evaluation score.
        task_id (int): The identifier for the associated task.
        created_at (date): The date of evaluation creation.
        task (Task): The task associated with this evaluation,
            establishing a relationship back to the Task model.
    """

    number: Mapped[int]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True, unique=True)
    created_at: Mapped[date] = mapped_column(
        Date, server_default=current_date(),
    )
    task: Mapped["Task"] = relationship("Task", back_populates="evaluation")

    def __init__(self, number, task_id, **kw: Any):
        """
        Initializes an Evaluation instance.

        Args:
            number (int): The evaluation score, which must be between 1 and 5.
            task_id (int): The identifier for the associated task.
            **kw (Any): Additional keyword arguments to be passed to the base class.

        Raises:
            ValueError: If the number is not between 1 and 5.
        """
        super().__init__(**kw)
        if number < 1 or number > 5:
            raise ValueError("Number must be between 1 and 5")
        self.number = number
        self.task_id = task_id
