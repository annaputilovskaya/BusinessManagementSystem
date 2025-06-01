from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator

from src.schemas.user_schemas import UserRead


class MeetingCreateSchema(BaseModel):
    """
    Meeting create schema.

    Attributes:
        meet_date (date): Date of the meeting.
        meet_time (time): Time of the meeting.
        participants (list(int)): User IDs who participate in the meeting.
    """

    meet_date: date = Field(ge=datetime.now().date())
    meet_time: time = Field(ge=time(8), le=time(20))
    participants: list[int]

    @model_validator(mode='after')
    def check_meeting_datetime(self):
        """
        Checks if meeting datetime is greater than current datetime.
        """
        meeting_datetime = datetime.combine(self.meet_date, self.meet_time)
        if meeting_datetime < datetime.now():
            raise ValueError("Meeting date and time must be in the future.")
        return self


class MeetingReadSchema(BaseModel):
    """
    Meeting read schema.

    Attributes:
        id: The identifier of the meeting.
        meet_date (date): Date of the meeting.
        meet_time (time): Time of the meeting.
        participants (list(UserReadSchema)): The list of users who participate in the meeting.
    """
    id: int
    meet_date: date
    meet_time: time
    participants: list[UserRead]
