from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        await self.accept()
        await self.channel_layer.group_add("notification", self.channel_name)

        # return await super().connect()
    async def disconnect(self, code):
        await self.channel_layer.group_discard("notification", self.channel_name)

        return await super().disconnect(code)
