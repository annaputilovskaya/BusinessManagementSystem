from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class EvaluationCreateSchema(BaseModel):
    """
    Evaluation create schema.

    Attributes:
        number (int): The evaluation score. Can take values from 1 to 5.
    """

    number: int = Field(ge=1, le=5)


class EvaluationReadSchema(EvaluationCreateSchema):
    """
    Evaluation read schema.

    Attributes:
        task_id (UUID): The identifier for the associated task.
        created_at (date): The date of evaluation creation.
    """

    created_at: date
    task_id: UUID
