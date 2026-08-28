import pytest
from game.services import (
    create_game_with_random_opponent,
    create_or_join_game_with_friend_opponent,
    create_game_with_computer_opponent,
)
from game.utils import create_new_game


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_game_with_random_opponent(playerA, playerB):
    opponent, game = await create_game_with_random_opponent(playerA.id)

    assert opponent == playerB
    assert game.playerA_id == playerA.id
    assert game.playerB_id == playerB.id


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_game_with_random_opponent_no_user_available(playerA):
    opponent, game = await create_game_with_random_opponent(playerA.id)

    assert opponent == None
    assert game == None


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_or_join_game_with_friend_opponent_creates_game(playerA):
    game = await create_or_join_game_with_friend_opponent(playerA.id, None)

    assert game is not None


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_or_join_game_with_friend_opponent_joins_game(playerA, playerB):
    game = await create_new_game(playerA.id)
    result = await create_or_join_game_with_friend_opponent(playerB.id, game.id)

    assert result.id == game.id


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_game_with_computer_opponent(playerA):
    computer, game = await create_game_with_computer_opponent(playerA.id)

    assert computer.is_human is False
    assert game.playerA_id == playerA.id
    assert game.playerB_id == computer.id
    assert computer.board.board.any()
