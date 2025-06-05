from datetime import date, time

from sqlalchemy import UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class MeetingUserAssociation(Base):
    """
    Meeting user relationship model in database.

    """

    __tablename__ = "meeting_user_association"
    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="idx_unique_meeting_user"),
    )

    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class Meeting(Base):
    """
    Meeting model.

    Attributes:
        meet_date (date): Date of the meeting.
        meet_time (time): Time of the meeting.
        is_canceled (bool): Indicates whether the meeting is canceled or not.
            Defaults to False.
        participants (list(User)): Users who participate in the meeting.
    """

    meet_date: Mapped[date]
    meet_time: Mapped[time]
    is_canceled: Mapped[bool] = mapped_column(Boolean, default=False)

    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="meeting_user_association",
        back_populates="meetings",
        cascade="all, delete",
        lazy="selectin",
    )

    def __str__(self):
        """
        Returns the string representation of the meeting object.
        """
        return f"{self.id}. {self.meet_date.isoformat()} {self.meet_time.isoformat()}"
