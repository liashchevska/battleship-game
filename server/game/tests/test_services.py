import pytest
from game.services import create_game_with_random_opponent


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
