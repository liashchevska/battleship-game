from game.models import Game, Player, Board
from channels.db import database_sync_to_async
from django.db.models import Q
from game.serializers import GameSerializer, YouSerializer
from game.computer import ComputerOpponent

def get_game_and_player(game_id, player_id):
    game = Game.objects.get(id=game_id)
    player = Player.objects.get(id=player_id)
    return game, player


@database_sync_to_async
def place_ships(player, ships, rows=10, cols=10):
    return player.create_board_and_place_ships(ships, rows, cols)


@database_sync_to_async
def create_new_game(playerA_id, playerB_id=None, rows=10, cols=10):
    return Game.create(playerA_id, playerB_id, rows, cols)


@database_sync_to_async
def add_player_to_game(game_id, player_id):
    game = Game.objects.get(id=game_id)
    return game.add_player_to_game(player_id)


@database_sync_to_async
def get_game_data(game_id, player_id):
    game, player = get_game_and_player(game_id, player_id)
    return GameSerializer(game, context={"player": player}).data


@database_sync_to_async
def get_player_data(player_id):
    player = Player.objects.get(id=player_id)
    return YouSerializer(player).data


@database_sync_to_async
def get_available_opponent(player_id):
    return Player.get_available_opponent(player_id)


@database_sync_to_async
def shoot_at(x, y, game_id, player_id):
    game, player = get_game_and_player(game_id, player_id)
    hit = game.shoot(player, x, y)
    return hit, game.is_over


@database_sync_to_async
def leave_game(player_id, game_id=None):
    Player.objects.get(id=player_id).leave_game(game_id)


@database_sync_to_async
def can_game_be_joined(game_id):
    return Game.objects.filter(
        Q(id=game_id), Q(playerA__isnull=True) | Q(playerB__isnull=True)
    ).exists()


@database_sync_to_async
def create_player(channel_name, is_human=True):
    return Player.objects.create(channel_name=channel_name, is_human=is_human)


@database_sync_to_async
def delete_player(player_id):
    Player.objects.get(id=player_id).delete()


@database_sync_to_async
def get_game(game_id):
    return Game.objects.get(id=game_id)


@database_sync_to_async
def generate_ships(rows=10, cols=10):
    return Board.generate_initial_board(rows, cols)


@database_sync_to_async
def computer_shoot(computer: ComputerOpponent) -> tuple[bool, bool]:
    return computer.shoot(), computer.game.is_over