import _asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotifyRequestConsumser(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notify", self.channel_name)
        print(f'Added {self.channel_name}')

    async def disconnect(self):
        await self.accept()
        await self.channel_layer.group_discard("notify", self.channel_name)
        print(f'Removed {self.channel_name}')