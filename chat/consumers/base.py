from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        pass

    async def receive_json(self, content, **kwargs):
        pass

    async def disconnect(self, code):
        pass
