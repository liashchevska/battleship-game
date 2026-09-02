import numpy as np
import pytest

from game.computer import ComputerOpponent


@pytest.fixture
def computer(gameWithComputer):
    return ComputerOpponent(gameWithComputer, gameWithComputer.playerB)


def test_get_cardinal_adjacen(computer):
    assert set(computer.get_cardinal_adjacent(0,0)) == {
        (0, 1),
        (1, 0),
    }

    assert set(computer.get_cardinal_adjacent(1, 1)) == {
        (0, 1),
        (1, 0),
        (1, 2),
        (2, 1),
    }


def test_get_next_coordinates_no_hits_calls_hunt(computer, mocker):
    mock_hunt = mocker.patch("game.computer.ComputerOpponent.hunt")
    mock_target = mocker.patch("game.computer.ComputerOpponent.target")

    computer.get_next_coordinates()
    mock_hunt.assert_called_once()
    mock_target.assert_not_called()


def test_get_next_coordinates_with_hits_calls_target(computer, mocker):
    mock_hunt = mocker.patch("game.computer.ComputerOpponent.hunt")
    mock_target = mocker.patch("game.computer.ComputerOpponent.target")
    computer.hits = [(0, 0)]

    computer.get_next_coordinates()
    mock_target.assert_called_once()
    mock_hunt.assert_not_called()


def test_target_chooses_only_unshot_cardinal_coordinate(computer, mocker):
    computer.hits = [(1, 1)]
    computer.target_board.shots[:] = 1
    computer.target_board.shots[1, 2] = 0

    mock_choice = mocker.patch("game.computer.random.choice")
    computer.target()
    mock_choice.assert_called_once_with([(1, 2)])


def test_shoot_miss_does_not_add_hit(computer, mocker):
    mocker.patch.object(computer.game, "shoot", return_value=(False))
    computer.shoot()

    assert computer.hits == []


def test_shoot_hit_adds_to_hits(computer, mocker):
    mocker.patch.object(computer, "get_next_coordinates", return_value=(1, 1))
    mocker.patch.object(computer.game, "shoot", return_value=(True))
    mocker.patch("game.computer.Coordinate.is_part_of_sunk_ship", return_value=False)
    computer.shoot()

    assert computer.hits == [(1, 1)]


def test_shoot_clears_hits_when_ship_is_sunk(computer, mocker):
    computer.hits = [(0, 0), (1, 0)]
    mocker.patch.object(computer.game, "shoot", return_value=(True))
    mocker.patch("game.computer.Coordinate.is_part_of_sunk_ship", return_value=True)
    computer.shoot()
    
    assert computer.hits == []

    
def test_orientation_unknown_with_one_hit(computer):
    computer.hits = [(2, 3)]
    assert computer.orientation is None


def test_orientation_vertical(computer):
    computer.hits = [(2, 3), (2, 4)]
    assert computer.orientation == "vertical"


def test_orientation_horizontal(computer):
    computer.hits = [(2, 3), (3, 3), (1, 3)]
    assert computer.orientation == "horizontal"
