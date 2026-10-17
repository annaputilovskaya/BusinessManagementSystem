from unittest.mock import AsyncMock

import pytest
from starlette.websockets import WebSocketDisconnect

from src.services.connection_manager import ConnectionManager


def test_connect_registers_room():
    manager = ConnectionManager()
    ws = AsyncMock()
    manager.connect(task_id="t1", user_id="u1", websocket=ws)
    assert manager.active_connections["t1"]["u1"] is ws


def test_disconnect_cleans_empty_room():
    manager = ConnectionManager()
    ws = AsyncMock()
    manager.connect(task_id="t1", user_id="u1", websocket=ws)
    manager.disconnect(task_id="t1", user_id="u1")
    assert "t1" not in manager.active_connections


def test_broadcast_only_to_same_room():
    manager = ConnectionManager()
    ws_own = AsyncMock()
    ws_other = AsyncMock()
    manager.connect(task_id="t1", user_id="u1", websocket=ws_own)
    manager.connect(task_id="t2", user_id="u2", websocket=ws_other)

    import anyio

    anyio.run(manager.broadcast, "t1", {"type": "comment", "text": "hi"})

    ws_own.send_json.assert_awaited_once()
    ws_other.send_json.assert_not_awaited()


def test_broadcast_tolerates_dead_socket():
    manager = ConnectionManager()
    dead = AsyncMock()
    dead.send_json.side_effect = RuntimeError("closed")
    manager.connect(task_id="t1", user_id="u1", websocket=dead)

    import anyio

    # не должно упасть
    anyio.run(manager.broadcast, "t1", {"type": "comment", "text": "x"})


def extract_token(headers):
    return headers["Authorization"].split()[1]


async def test_ws_history_on_connect(client, make_team, make_user, make_task, login):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id, user_id=manager.id)
    token = extract_token(login(manager))

    with client.websocket_connect(f"/tasks/{task.id}/comments/?token={token}") as ws:
        history = ws.receive_json()
    assert isinstance(history, list)


async def test_ws_broadcast_between_members(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id)
    token_manager = extract_token(login(manager))
    token_executor = extract_token(login(executor))

    with client.websocket_connect(
        f"/tasks/{task.id}/comments/?token={token_manager}"
    ) as ws1:
        ws1.receive_json()  # history
        with client.websocket_connect(
            f"/tasks/{task.id}/comments/?token={token_executor}"
        ) as ws2:
            ws2.receive_json()  # history

            ws1.send_json({"text": "hello team"})
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

    assert msg1["type"] == "comment"
    assert msg1["text"] == "hello team"
    assert msg1["user_id"] == str(manager.id)
    assert msg2 == msg1


async def test_ws_broadcast_not_leaked_to_other_task(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task_a = await make_task(team_id=team.id, name="A")
    task_b = await make_task(team_id=team.id, name="B")
    token = extract_token(login(manager))

    with client.websocket_connect(
        f"/tasks/{task_a.id}/comments/?token={token}"
    ) as ws_a:
        ws_a.receive_json()  # history
        with client.websocket_connect(
            f"/tasks/{task_b.id}/comments/?token={token}"
        ) as ws_b:
            ws_b.receive_json()  # history

            ws_a.send_json({"text": "for A only"})
            msg = ws_a.receive_json()
            assert msg["text"] == "for A only"

            # на B не должно прийти сообщение из A:
            # следующий receive на B — либо зависнет (timeout в TestClient),
            # либо получит новый корректный фрейм после send с B.
            ws_b.send_json({"text": "for B"})
            msg_b = ws_b.receive_json()
            assert msg_b["text"] == "for B"


async def test_ws_rejects_outsider_team(client, make_team, make_user, make_task, login):
    team = await make_team()
    owner = await make_user(team_id=team.id)
    outsider = await make_user()  # без команды
    task = await make_task(team_id=team.id, user_id=owner.id)
    token = extract_token(login(outsider))

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(
            f"/tasks/{task.id}/comments/?token={token}"
        ) as ws:
            ws.receive_json()
    assert exc.value.code == 1008


async def test_ws_rejects_missing_token(client, make_team, make_task):
    team = await make_team()
    task = await make_task(team_id=team.id)

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/tasks/{task.id}/comments/") as ws:
            ws.receive_json()
    assert exc.value.code == 1008


async def test_ws_invalid_json_returns_error_and_stays_open(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id, user_id=manager.id)
    token = extract_token(login(manager))

    with client.websocket_connect(f"/tasks/{task.id}/comments/?token={token}") as ws:
        ws.receive_json()  # history
        ws.send_text("not a json")
        err = ws.receive_json()
        assert err["type"] == "error"

        ws.send_json({"text": "valid after error"})
        msg = ws.receive_json()
        assert msg["type"] == "comment"
        assert msg["text"] == "valid after error"


async def test_ws_comment_persisted_to_db(
    client, make_team, make_user, make_task, login, test_engine
):
    from sqlalchemy import select

    from src.models import Comment

    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id, user_id=manager.id)
    token = extract_token(login(manager))

    with client.websocket_connect(f"/tasks/{task.id}/comments/?token={token}") as ws:
        ws.receive_json()
        ws.send_json({"text": "persist me"})
        ws.receive_json()

    from sqlalchemy.ext.asyncio import async_sessionmaker

    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        comments = (
            await session.scalars(select(Comment).where(Comment.task_id == task.id))
        ).all()
    assert len(comments) == 1
    assert comments[0].text == "persist me"
    assert comments[0].user_id == manager.id
