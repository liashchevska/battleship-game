from enum import StrEnum
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio

from game.services import (
    create_random_game,
    create_or_join_friend_game,
    create_computer_game,
)
from game.utils import (
    place_ships,
    get_game_data,
    get_player_data,
    shoot_at,
    leave_game,
    can_game_be_joined,
    delete_player,
    create_player,
    computer_shoot
)
from game.computer import ComputerOpponent


class OpponentType(StrEnum):
    RANDOM = "random"
    FRIEND = "friend"
    COMPUTER = "computer"


class EventType(StrEnum):
    START = "game.start"
    WAIT = "game.wait"
    UPDATE = "game.update"
    INVALID = "game.invalid"
    LEAVE = "game.leave"


class ActionType(StrEnum):
    START = "start"
    SHOOT = "shoot"
    LEAVE = "leave"


class GameConsumer(AsyncJsonWebsocketConsumer):
    @property
    def game_group(self):
        return None if self.game_id is None else f"game_no_{self.game_id}"

    @property
    def is_computer_opponent(self):
        return self.computer is not None

    async def get_serialized_game(self):
        return await get_game_data(self.game_id, self.player.id)

    async def get_serialized_player(self):
        return await get_player_data(self.player.id)

    async def connect(self):
        self.player = await create_player(self.channel_name)
        self.game_id = None
        self.computer = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id is not None:
            await self.leave()
        await delete_player(self.player.id)

    async def broadcast_to_group(self, *, type, action=None, **data):
        await self.channel_layer.group_send(
            self.game_group, {"type": type, "action": action, **data}
        )

    async def send_to_client(self, *, action, **data):
        await self.send_json({"action": action, **data})

    async def add_players_to_game_group(self, *players):
        for player in players:
            await self.channel_layer.group_add(self.game_group, player.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action == ActionType.START:
            await self.start(
                content["ships"],
                content["opponent_type"],
                content["game_to_join_id"],
            )
        elif action == ActionType.SHOOT:
            await self.shoot(content["x"], content["y"])
        elif action == ActionType.LEAVE:
            await self.leave()

    async def start(self, ships, opponent_type, game_to_join_id):
        if game_to_join_id is not None and not await can_game_be_joined(
            game_to_join_id
        ):
            await self.send_json({"type": EventType.INVALID})
            return
        await place_ships(self.player, ships)

        if opponent_type == OpponentType.FRIEND:
            await self.start_friend_game(game_to_join_id)
        elif opponent_type == OpponentType.COMPUTER:
            await self.start_computer_game()
        else:
            await self.start_random_game()

    async def start_friend_game(self, game_to_join_id):
        game = await create_or_join_friend_game(self.player.id, game_to_join_id) #fmt: skip
        self.game_id = game.id
        await self.add_players_to_game_group(self.player)

        if game_to_join_id is None:
            await self.broadcast_to_group(type=EventType.WAIT, game_id=self.game_id)
        else:
            await self.broadcast_to_group(
                type=EventType.UPDATE,
                action=EventType.START,
                game_id=self.game_id
            )

    async def start_computer_game(self):
        opponent, game = await create_computer_game(self.player.id)
        self.game_id = game.id
        self.computer = ComputerOpponent(game, opponent)

        await self.add_players_to_game_group(self.player)
        await self.broadcast_to_group(
            type=EventType.UPDATE,
            action=EventType.START,
            game_id=self.game_id,
        )

    async def start_random_game(self):
        opponent, game = await create_random_game(self.player.id)

        if opponent is None:
            await self.game_wait({"type": EventType.WAIT, "game_id": None})

        else:
            self.game_id = game.id
            await self.add_players_to_game_group(self.player, opponent)
            await self.broadcast_to_group(
                type=EventType.UPDATE,
                action=EventType.START,
                game_id=self.game_id
            )

    async def shoot(self, x, y):
        hit, _ = await shoot_at(x, y, self.game_id, self.player.id)

        if self.is_computer_opponent:
            await self.send_to_client(
                action=EventType.UPDATE,
                game=await self.get_serialized_game()
            )
            if not hit:
                await self.computer_turn()
            return

        await self.broadcast_to_group(
            type=EventType.UPDATE,
            action=EventType.UPDATE,
            game_id=self.game_id
        )

    async def computer_turn(self):
        while True:
            await asyncio.sleep(0.5)

            hit, is_over = await computer_shoot(self.computer)

            await self.send_to_client(
                action=EventType.UPDATE,
                game=await self.get_serialized_game()
            )

            if not hit or is_over:
                break

    async def leave(self):
        if self.game_id is not None:
            await self.channel_layer.group_discard(
                self.game_group,
                self.channel_name,
            )
            await self.broadcast_to_group(type=EventType.LEAVE)

        await leave_game(self.player.id, self.game_id)
        self.game_id = None
        self.computer = None

    async def game_update(self, event):
        if event["action"] == EventType.START:
            self.game_id = event["game_id"]

        await self.send_to_client(
            action=event["action"],
            game=await self.get_serialized_game()
        )

    async def game_wait(self, event):
        await self.send_to_client(
            action=event["type"],
            game_id=self.game_id,
            you=await self.get_serialized_player(),
        )

    async def game_leave(self, event):
        await self.send_to_client(action=event["type"])
        await self.leave()
