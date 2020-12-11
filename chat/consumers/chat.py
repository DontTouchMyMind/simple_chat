from channels.db import database_sync_to_async

from chat.consumers import BaseChatConsumer
from chat.models import ChatGroup


class ChatConsumer(BaseChatConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.participants = []
        self.channel = f'group_{self.group_id}'

    async def connect(self):
        await super().connect()
        group = await self.get_group()
        if not group:
            await self._throw_error({'detail': 'Group not found'})
            # await
        await self.channel_layer.group_add(self.channel, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.channel, self.channel_name)
        await super().disconnect(code=code)

    @database_sync_to_async
    def get_group(self):
        group = ChatGroup.objects.filter(pk=self.group_id).first()
        if group:
            self.group = group
        return group
