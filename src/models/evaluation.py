from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Evaluation(Base):
    """Evaluation model representing the assessment of tasks.

    Attributes:
        number (SmallInteger): The evaluation score.
        task_id (int): The identifier for the associated task.
        task (Task): The task associated with this evaluation,
            establishing a relationship back to the Task model.
    """

    number: Mapped[int]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

    task: Mapped["Task"] = relationship("Task", back_populates="evaluation")

    def __init__(self, number, task_id, **kw: Any):
        super().__init__(**kw)
        if number < 1 or number > 5:
            raise ValueError("Number must be between 1 and 5")
        self.number = number
        self.task_id = task_id
