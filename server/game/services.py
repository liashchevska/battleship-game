from game.models import Player, Game
from game.utils import get_available_opponent, create_new_game, add_player_to_game, get_game, create_player, shoot_at, place_ships, generate_ships

async def create_random_game(creator_id: int) -> tuple[Player, Game] | tuple[None, None]: # fmt: skip
    opponent = await get_available_opponent(creator_id)
    game = None
    
    if opponent is not None:
        game = await create_new_game(creator_id, opponent.id)
    
    return opponent, game


async def create_or_join_friend_game(player_id: int | None, game_id: int | None) -> Game:
    if game_id is None:
       return await create_new_game(player_id)
    
    await add_player_to_game(game_id, player_id)
    return await get_game(game_id)


async def create_computer_game(player_id: int) -> tuple[Player, Game]:
    computer = await create_player(None, is_human=False)
    ships = await generate_ships()
    await place_ships(computer, ships)
    return computer, await create_new_game(player_id, computer.id)
