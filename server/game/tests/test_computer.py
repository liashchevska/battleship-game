from game.computer import ComputerOpponent


def test_does_not_choose_same_coordinates_twice():
    size = 5
    opponent = ComputerOpponent(
        player_object_id=1,
        rows=size,
        cols=size,
    )

    coordinates = [opponent.choose_coordinates() for _ in range(size ** 2)]

    assert len(coordinates) == len(set(coordinates))
