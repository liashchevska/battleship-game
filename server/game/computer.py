import random
import numpy as np
from game.models import Coordinate

class ComputerOpponent:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.hits = []

    @property
    def target_board(self):
        return self.game.playerA.board

    @property
    def not_shot(self):
        sunk_ships = self.target_board.shot_ships
        return np.argwhere(self.target_board.get_shots_with_marked(sunk_ships) == 0)

    @property
    def orientation(self) -> None | str:
        if len(self.hits) < 2:
            return None

        if self.hits[0][0] == self.hits[1][0]:
            return "vertical"

        return "horizontal"


    def get_cardinal_adjacent(self, x, y):
        coordinates = []
        for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_x, adj_y = x + offset_x, y + offset_y
            if 0 <= adj_x < self.game.rows and 0 <= adj_y < self.game.cols:
                coordinates.append((adj_x, adj_y))   
        return coordinates
    

    def hunt(self) -> tuple[int, int]:
        x, y = random.choice(self.not_shot)
        return int(x), int(y)

    def target(self):
        if self.orientation == "vertical":
            x = self.hits[0][0]
            ys = [y for _, y in self.hits]

            targeted = [
                (x, min(ys) - 1),
                (x, max(ys) + 1),
            ]
        elif self.orientation == "horizontal":
            y = self.hits[0][1]
            xs = [x for x, _ in self.hits]

            targeted = [
                (min(xs) - 1, y),
                (max(xs) + 1, y),
            ]
        else:
            targeted = self.get_cardinal_adjacent(*self.hits[-1])

        available = [
            coordinate
            for coordinate in targeted
            if (
                0 <= coordinate[0] < self.game.rows
                and 0 <= coordinate[1] < self.game.cols
                and self.target_board.shots[coordinate] == 0
            )
        ]

        return random.choice(available)


    def get_next_coordinates(self):
        if self.hits:
            return self.target()
        return self.hunt()

    def shoot(self):
        self.game.refresh_from_db()
        x, y = self.get_next_coordinates()
        hit = self.game.shoot(self.player, x, y)
        if hit:
            self.hits.append((x, y))
            sunk = Coordinate.is_part_of_sunk_ship(self.target_board.id, x, y)            
            if sunk:
                self.hits.clear()
        
        return hit