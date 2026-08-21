from game.models import Player, Game
from game.utils import get_available_opponent, create_new_game

async def create_game_with_random_opponent(creator_id: int) -> tuple[Player, Game] | tuple[None, None]: # fmt: skip
    opponent = await get_available_opponent(creator_id)
    game = None
    
    if opponent is not None:
        game = await create_new_game(creator_id, opponent.id)
    
    return opponent, game
