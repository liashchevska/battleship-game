import pytest
from game.models import Game, Player, Ship, Board

@pytest.fixture
def player_factory(db):
    def create_player(channel, is_human=True):
        return Player.create(channel_name=channel, is_human=is_human)

    return create_player


# board


@pytest.fixture
def board_factory(db):
    def create_board(
        player,
        rows=10,
        cols=10,
    ):
        return Board.create(player, rows, cols)

    return create_board


@pytest.fixture
def board10x10(db, board_factory, player_factory):
    return board_factory(player_factory("channel"))


@pytest.fixture
def ship_factory(db, board10x10):
    def create_ship(x, y, rows, cols):
        ship = Ship.objects.create(x=x, y=y, rows=rows, cols=cols, board=board10x10)
        Ship.add_coordinates(ship)
        return ship

    return create_ship


@pytest.fixture
def ship1x4_at0x0(db, ship_factory):
    return ship_factory(0, 0, 1, 4)


@pytest.fixture
def ship2x1_at4x4(db, ship_factory):
    return ship_factory(4, 4, 2, 1)


@pytest.fixture
def game_factory(db):
    def create_game(rows, cols, playerA_id=None, playerB_id=None):
        return Game.create(playerA_id, playerB_id, rows, cols)

    return create_game


@pytest.fixture
def gameAB(db, game_factory, board_factory, player_factory):
    playerA = board_factory(player_factory("channelA")).player
    playerB = board_factory(player_factory("channelB")).player
    return game_factory(10, 10, playerA.id, playerB.id)


@pytest.fixture
def game(db, game_factory):
    return game_factory(10, 10)


@pytest.fixture
def playerA(db, board_factory, player_factory):
    board = board_factory(player_factory(channel="a"))
    return board.player


@pytest.fixture
def playerB(db, board_factory, player_factory):
    board = board_factory(player_factory(channel="b"))
    return board.player


@pytest.fixture
def playerC(db, player_factory):
    return player_factory(channel="c")


@pytest.fixture
def playerComputer(player_factory):
    return player_factory(None, False)
