from enum import Enum

class StatusEnum(Enum):
    """Task status enum."""

    OPENED = "opened"
    PROGRESS = "progress"
    DONE = "done"
