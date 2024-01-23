import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notifications", self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def send_notifications(self, event):
        message = event['content']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'content': message
        }))
