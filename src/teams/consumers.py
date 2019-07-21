from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
from .models import Invitation


class InvitationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("invite", self.channel_name)
        print(f"Added {self.channel_name}")

    async def disconnect(self):
        await self.channel_layer.group_discard("invite", self.channel_name)
        print(f"Removed Invitation {self.channel_name}")

    async def user_invite(self, event):
        await self.send_json(event)
        print(f"Got invitation {event} at {self.channel_name}")
