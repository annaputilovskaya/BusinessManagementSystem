from datetime import date, time

from src.schemas.task_schemas import CommentCreate
from src.services.meeting_services import cancel_meeting, check_schedule_conflict
from src.services.task_services import create_comment


async def test_check_schedule_conflict_empty_participants():
    class FakeSession:
        async def scalars(self, *_args, **_kwargs):
            return []

    conflicts = await check_schedule_conflict(
        participant_ids=[],
        meeting_date=date(2030, 1, 1),
        meeting_time=time(10),
        session=FakeSession(),
    )
    assert conflicts == []


async def test_check_schedule_conflict_midnight_boundaries_do_not_raise():
    class FakeSession:
        async def scalars(self, *_args, **_kwargs):
            return []

    for moment in (time(0, 30), time(23, 30)):
        conflicts = await check_schedule_conflict(
            participant_ids=["user-1"],
            meeting_date=date(2030, 1, 1),
            meeting_time=moment,
            session=FakeSession(),
        )
        assert conflicts == []


async def test_check_schedule_conflict_detects_nearby_meeting():
    class M:
        def __init__(self, d, t):
            self.meet_date = d
            self.meet_time = t

    class FakeSession:
        async def scalars(self, *_args, **_kwargs):
            return [M(date(2030, 1, 1), time(10, 30))]

    conflicts = await check_schedule_conflict(
        participant_ids=["user-1"],
        meeting_date=date(2030, 1, 1),
        meeting_time=time(10, 0),
        session=FakeSession(),
    )
    assert len(conflicts) == 1


def test_create_comment_sets_text_and_ids():
    class U:
        id = "user-1"

    comment = create_comment(CommentCreate(text="hello"), task_id="task-1", user=U())
    assert comment.text == "hello"
    assert comment.task_id == "task-1"
    assert comment.user_id == "user-1"


async def test_cancel_meeting_sets_flag():
    class FakeSession:
        def __init__(self):
            self.committed = False

        async def commit(self):
            self.committed = True

    class M:
        is_canceled = False

    meeting = M()
    session = FakeSession()
    result = await cancel_meeting(meeting, session)
    assert meeting.is_canceled is True
    assert session.committed is True
    assert result == {"detail": "Meeting canceled."}
