from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.services import (
    create_game_with_random_opponent,
    create_or_join_game_with_friend_opponent,
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
)
from enum import StrEnum


class EventType(StrEnum):
    START = "game.start"
    WAIT = "game.wait"
    UPDATE = "game.update"
    INVALID = "game.invalid"


class ActionType(StrEnum):
    START = "start"
    SHOOT = "shoot"
    LEAVE = "leave"


class GameConsumer(AsyncJsonWebsocketConsumer):
    @property
    def game_group(self):
        return None if self.game_id is None else f'Game_{self.game_id}'

    async def connect(self):
        self.player = await create_player(self.channel_name)        
        self.player_id = self.player.id
        self.game_id = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id is not None:
            await self.leave()
        await delete_player(self.player_id)

    async def add_players_to_game_group(self, *players):
        for player in players:
            await self.channel_layer.group_add(self.game_group, player.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', None)
        if action == ActionType.START: 
            await self.start(content['ships'],
                             content['friend_as_opponent'],
                             content['game_to_join_id'])
        elif action == ActionType.SHOOT:
            await self.shoot(content['x'],
                             content['y'])
        elif action == ActionType.LEAVE:
            await self.leave()

    async def start(self, ships, friend_as_opponent, game_to_join_id):
        if game_to_join_id is not None and not await can_game_be_joined(game_to_join_id):
            await self.send_json({'type': EventType.INVALID})
            return
        await place_ships(self.player, ships)
        if friend_as_opponent:
            await self.game_with_a_friend_opponent(game_to_join_id)
        else:
            await self.game_with_a_random_opponent()

    async def game_with_a_friend_opponent(self, game_to_join_id):
        game = await create_or_join_game_with_friend_opponent(self.player_id, game_to_join_id) #fmt: skip
        self.game_id = game.id
        await self.add_players_to_game_group(self.player)

        if game_to_join_id is None:
            await self.broadcast(type=EventType.WAIT, game_id=self.game_id)        
        else:
            await self.broadcast(type=EventType.UPDATE, action=EventType.START, game_id=self.game_id)        

    async def game_with_a_random_opponent(self):
        opponent, game = await create_game_with_random_opponent(self.player_id)

        if opponent is None:
            await self.game_wait({"type": EventType.WAIT, "game_id": None})

        else:
            self.game_id = game.id
            await self.add_players_to_game_group(self.player, opponent)
            await self.broadcast(type=EventType.UPDATE, action=EventType.START, game_id=self.game_id)        

    async def shoot(self, x, y):
        await shoot_at(x, y, self.game_id, self.player_id)
        await self.broadcast(type=EventType.UPDATE, action=EventType.UPDATE, game_id=self.game_id)        

    async def leave(self):
        if self.game_id is not None:
            await self.channel_layer.group_discard(
                self.game_group,
                self.channel_name,
            )
            await self.broadcast(type="game.leave")

        await leave_game(self.player_id, self.game_id)
        self.game_id = None

    async def game_update(self, event):
        if event['action'] == EventType.START:
            self.game_id = event['game_id']

        data = await get_game_data(event['game_id'], self.player_id)
        await self.send_json({'action': event['action'],
                              'game': data})

    async def game_wait(self, event):
        data = await get_player_data(self.player_id)
        await self.send_json({'action': event['type'],
                              'game_id': self.game_id,
                              'you': data})

    async def game_leave(self, event):
        await self.send_json({'action': event['type']})
        await self.leave()

    async def broadcast(self, *, type, action=None, **data):
        await self.channel_layer.group_send(
            self.game_group, {"type": type, "action": action, **data}
        )
