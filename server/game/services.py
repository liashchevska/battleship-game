from game.models import Player, Game
from game.utils import get_available_opponent, create_new_game, add_player_to_game, get_game

async def create_game_with_random_opponent(creator_id: int) -> tuple[Player, Game] | tuple[None, None]: # fmt: skip
    opponent = await get_available_opponent(creator_id)
    game = None
    
    if opponent is not None:
        game = await create_new_game(creator_id, opponent.id)
    
    return opponent, game


async def create_or_join_game_with_friend_opponent(player_id: int | None, game_id: int | None) -> Game:
    if game_id is None:
       return await create_new_game(player_id)
    
    await add_player_to_game(game_id, player_id)
    return await get_game(game_id)
