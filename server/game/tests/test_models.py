from game.models import Board, Ship, Coordinate, Game, Player
import numpy as np
import pytest
from django.forms.models import model_to_dict

array10x10_empty = np.zeros((10, 10), dtype=np.int8)
array10x10_1x1_at4x4 = array10x10_empty.copy()
array10x10_1x1_at4x4[4:5, 4:5] = 1


ship1x3_at4x4_data = {"x": 4, "y": 4, "rows": 1, "cols": 3}
ship1x1_at0x0_data = {"x": 0, "y": 0, "rows": 1, "cols": 1}
ship_invalid = {"x": -1, "y": 0, "rows": 1, "cols": 1}

@pytest.mark.django_db
@pytest.mark.parametrize(
    "array, x, y, rows, cols, expected",
    [
        (array10x10_empty, 0, 0, 3, 1, True),
        (array10x10_empty, 6, 6, 3, 1, True),
        (array10x10_empty, 0, 9, 1, 3, False),
        (array10x10_empty, 9, 0, 3, 1, False),
        (array10x10_1x1_at4x4, 4, 4, 1, 1, False),
        (array10x10_1x1_at4x4, 5, 5, 1, 1, False),
        (array10x10_1x1_at4x4, 5, 5, 1, 2, False),
        (array10x10_1x1_at4x4, 6, 6, 1, 1, True),
    ],
)
def test_board_is_placement_possible_boundaries(array, x, y, rows, cols, expected):
    assert Board.is_placement_possible(array, x, y, rows, cols) == expected

@pytest.mark.django_db
def test_board_add_ships_to_db(board10x10):
    assert Ship.objects.filter(board=board10x10).count() == 0
    ship = board10x10.add_ships_to_db(ship1x3_at4x4_data)[0]
    assert Ship.objects.filter(board=board10x10).count() == 1
    assert ship.coordinate_set.all().count() == 3

@pytest.mark.django_db
def test_board_ships_alive(board10x10):
    board10x10.add_ships_to_db(ship1x3_at4x4_data)
    assert board10x10.ships_alive == 1
    board10x10.add_ships_to_db(ship1x1_at0x0_data)
    assert board10x10.ships_alive == 2

@pytest.mark.django_db
def test_board_all_ships_are_shot(board10x10):
    ship = board10x10.add_ships_to_db(ship1x3_at4x4_data)[0]
    assert not board10x10.all_ships_are_shot
    ship.coordinate_set.all().update(is_hit=True)
    assert board10x10.all_ships_are_shot

@pytest.mark.django_db
def test_board_mark_surrounding_cells(board10x10):
    board10x10.place_ships(ship1x1_at0x0_data)
    ship = board10x10.ship_set.all()[0]
    marked = Board._mark_surrounding_cells(board10x10.shots, model_to_dict(ship))
    assert marked[marked == Board.MISS].size == 3

@pytest.mark.django_db
def test_board_get_shots_with_marked(board10x10):
    # marks surrounding cells only for sunken ships
    board10x10.place_ships(ship1x3_at4x4_data)
    ship = board10x10.ship_set.all()[0]
    shots_with_marked = board10x10.get_shots_with_marked(board10x10.shot_ships)
    assert shots_with_marked[shots_with_marked == Board.MISS].size == 0
    ship.coordinate_set.all().update(is_hit=True)
    shots_with_marked = board10x10.get_shots_with_marked(board10x10.shot_ships)
    assert shots_with_marked[shots_with_marked == Board.MISS].size == 12

@pytest.mark.django_db
def test_board_place_ships(board10x10):
    assert board10x10.place_ships(ship1x1_at0x0_data)
    assert not board10x10.place_ships(ship_invalid)

@pytest.mark.django_db
def test_board_shoot(board10x10):
    board10x10.place_ships(ship1x1_at0x0_data)
    assert not board10x10.shoot(1, 1)
    assert board10x10.shoot(0, 0)
    assert board10x10.shots[0, 0] == 2
    assert Coordinate.objects.get(x=0, y=0, ship__board=board10x10).is_hit

@pytest.mark.django_db
def test_board_is_already_shot(board10x10):
    assert not board10x10.is_already_shot(1, 1)
    board10x10.shots[1, 1] = 1
    board10x10.save()
    assert board10x10.is_already_shot(1, 1)

@pytest.mark.django_db
@pytest.mark.parametrize(
    "rows, cols, expected",
    [
        (10, 10, 4),
        (10, 15, 4),
        (15, 15, 5),
        (20, 15, 5),
        (20, 20, 6),
    ],
)
def test_board_get_number_of_ships_per_player(rows, cols, expected):
    assert Board.get_number_of_ships_per_player(rows, cols) == expected

@pytest.mark.django_db
def test_board_generate_initial_board(board10x10):
    ships_data = Board.generate_initial_board(10, 10)
    assert board10x10.place_ships(*ships_data)


# ship

@pytest.mark.django_db
def test_ship_length(ship1x4_at0x0, ship2x1_at4x4):
    assert ship1x4_at0x0.length == 4
    assert ship2x1_at4x4.length == 2

@pytest.mark.django_db
def test_ship_orientation(ship1x4_at0x0, ship2x1_at4x4):
    assert ship1x4_at0x0.orientation == "HR"
    assert ship2x1_at4x4.orientation == "VR"

@pytest.mark.django_db
def test_ship_indicies(ship2x1_at4x4):
    assert ship2x1_at4x4.indicies == (slice(4, 6), slice(4, 5))

@pytest.mark.django_db
def test_ship_generate_random_ship(db):
    rows, cols = Ship.generate_random_ship(length=3).values()
    assert (rows == 3 and cols == 1) or (rows == 1 and cols == 3)


# game

@pytest.mark.django_db
def test_game_end_game(gameAB):
    assert not gameAB.is_over
    gameAB.end_game()
    assert gameAB.is_over

@pytest.mark.django_db
def test_game_next_player(gameAB):
    assert gameAB.current == gameAB.playerA
    gameAB.next_player()
    assert gameAB.current == gameAB.playerB

@pytest.mark.django_db
def test_game_add_player_to_game(game, playerA, playerB, playerC):
    assert game.add_player_to_game(playerA.id)
    assert game.playerA.id == playerA.id
    assert game.add_player_to_game(playerB.id)
    assert game.playerB.id == playerB.id
    assert not game.add_player_to_game(playerC.id)

@pytest.mark.django_db
def test_game_shoot(gameAB):
    gameAB.playerB.board.place_ships(ship1x1_at0x0_data)
    gameAB.playerA.board.place_ships(ship1x1_at0x0_data)

    assert gameAB.current == gameAB.playerA
    gameAB.shoot(gameAB.playerB, 0, 0)
    assert gameAB.current == gameAB.playerA
    gameAB.shoot(gameAB.playerA, 1, 1)
    assert gameAB.current == gameAB.playerB
    gameAB.shoot(gameAB.playerB, 0, 0)
    assert gameAB.current == gameAB.playerB
    assert gameAB.is_over
    assert gameAB.winner is gameAB.playerB


# player

@pytest.mark.django_db
def test_player_get_random_available_player(playerA, playerB):
    assert Player.get_available_opponent(playerA.id).id is playerB.id
    assert Player.get_available_opponent(playerB.id).id is playerA.id
    playerB.set_busy_status()
    assert Player.get_available_opponent(playerA.id) is None

@pytest.mark.django_db
def test_get_random_available_player_ignores_computer(playerA, playerComputer):
    assert Player.get_available_opponent(playerA.id) is None

@pytest.mark.django_db
def test_player_create_board_and_place_ships(playerC):
    playerC.create_board_and_place_ships([ship1x3_at4x4_data], 10, 10)
    assert Board.objects.all().count() == 1
    assert Ship.objects.all().count() == 1
    assert Coordinate.objects.count() == 3

@pytest.mark.django_db
def test_player_update_player_statuses(playerA):  # fmt: skip
    assert not playerA.is_busy
    Player.update_players_statuses(playerA.id, None)
    assert Player.objects.get(pk=playerA.id).is_busy

@pytest.mark.django_db
def test_player_leave_game(gameAB):
    playerA, playerB = gameAB.playerA, gameAB.playerB
    assert Board.objects.filter(player=playerA).count() == 1
    assert Board.objects.filter(player=playerB).count() == 1
    assert Game.objects.all().count() == 1

    playerA.leave_game(gameAB.id)
    assert Board.objects.filter(player=playerA).count() == 0
    assert Game.objects.all().count() == 0

    playerB.leave_game(gameAB.id)
    assert Board.objects.filter(player=playerB).count() == 0
