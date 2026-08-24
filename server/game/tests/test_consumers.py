import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from contextlib import asynccontextmanager
from game.consumers import GameConsumer
from game.models import Player, Game


@pytest.fixture
def communicator():
    @asynccontextmanager
    async def create(URL="/ws/game/"):
        communicator = WebsocketCommunicator(GameConsumer.as_asgi(), URL)
        connected, _ = await communicator.connect()
        assert connected

        try:
            yield communicator
        finally:
            await communicator.disconnect()

    return create


@pytest.fixture
def game(communicator):
    @asynccontextmanager
    async def create():
        async with communicator() as playerA, communicator() as playerB:
            await playerA.send_json_to(
                {
                    "action": "start",
                    "ships": [],
                    "friend_as_opponent": False,
                    "game_to_join_id": None,
                }
            )

            await playerA.receive_json_from()

            await playerB.send_json_to(
                {
                    "action": "start",
                    "ships": [],
                    "friend_as_opponent": False,
                    "game_to_join_id": None,
                }
            )

            await playerA.receive_json_from()
            await playerB.receive_json_from()

            yield playerA, playerB

    return create


@pytest.mark.django_db()
@pytest.mark.asyncio
async def test_player_lifecycle():
    assert await Player.objects.acount() == 0

    communicator = WebsocketCommunicator(GameConsumer.as_asgi(), "/ws/game/")
    connected, _ = await communicator.connect()

    assert connected
    assert await database_sync_to_async(Player.objects.count)() == 1

    await communicator.disconnect()
    assert await database_sync_to_async(Player.objects.count)() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_join_game_by_invalid_game_id(communicator):
    async with communicator() as client:
        await client.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": 999999,
            }
        )
        response = await client.receive_json_from()
        assert response == {"type": "game.invalid"}


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_players_can_create_and_join_friend_game(communicator):
    async with communicator() as playerA, communicator() as playerB:
        # Player A creates the friend game.
        await playerA.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()
        assert responseA["action"] == "game.wait"

        game_id = responseA["game_id"]

        # Player B joins the game.
        await playerB.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": game_id,
            }
        )

        responseA = await playerA.receive_json_from()
        responseB = await playerB.receive_json_from()

        assert responseA["action"] == "game.start"
        assert responseB["action"] == "game.start"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_players_can_start_random_game(communicator):
    async with communicator() as playerA, communicator() as playerB:
        await playerA.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": False,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()

        assert responseA["action"] == "game.wait"
        assert responseA["game_id"] is None

        await playerB.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": False,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()
        responseB = await playerB.receive_json_from()

        assert responseA["action"] == "game.start"
        assert responseB["action"] == "game.start"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_players_can_start_random_game(communicator):
    async with communicator() as playerA, communicator() as playerB:
        await playerA.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": False,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()

        assert responseA["action"] == "game.wait"
        assert responseA["game_id"] is None

        await playerB.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": False,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()
        responseB = await playerB.receive_json_from()

        assert responseA["action"] == "game.start"
        assert responseB["action"] == "game.start"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_join_game_that_is_already_joined(communicator):
    async with (
        communicator() as playerA,
        communicator() as playerB,
        communicator() as playerC,
    ):
        # Player A creates the friend game.
        await playerA.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": None,
            }
        )

        responseA = await playerA.receive_json_from()
        game_id = responseA["game_id"]

        # Player B joins the game.
        await playerB.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": game_id,
            }
        )

        await playerA.receive_json_from()
        await playerB.receive_json_from()

        # Player C tries to join the already occupied game.
        await playerC.send_json_to(
            {
                "action": "start",
                "ships": [],
                "friend_as_opponent": True,
                "game_to_join_id": game_id,
            }
        )

        responseC = await playerC.receive_json_from()
        assert responseC == {
            "type": "game.invalid",
        }


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_player_can_shoot(game):
    async with game() as (playerA, playerB):
        await playerA.send_json_to(
            {
                "action": "shoot",
                "x": 0,
                "y": 0,
            }
        )

        response = await playerB.receive_json_from()

        assert response["action"] == "game.update"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_player_can_leave_game(game):
    async with game() as (playerA, playerB):
        await playerA.send_json_to(
            {
                "action": "leave",
            }
        )

        response = await playerB.receive_json_from()

        assert response["action"] == "game.leave"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_disconnect_leaves_game_and_deletes_player(game):
    async with game() as (playerA, playerB):
        await playerA.disconnect()

        response = await playerB.receive_json_from()

        assert response["action"] == "game.leave"
