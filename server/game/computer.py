import random


class ComputerOpponent:
    def __init__(self, player_object_id, rows=10, cols=10):
        self.player_object_id = player_object_id
        self.rows = rows
        self.cols = cols
        self.shots = set()
        # self.hits = []

    def choose_coordinates(self) -> tuple[int, int]:
        available = [
            (x, y)
            for x in range(self.rows)
            for y in range(self.cols)
            if (x, y) not in self.shots
        ]

        coordinates = random.choice(available)
        self.shots.add(coordinates)
        return coordinates
