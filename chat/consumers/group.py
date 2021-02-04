from channels.db import database_sync_to_async

from chat.consumers import BaseChatConsumer
from chat.models import ChatGroup, GroupParticipant, User


class GroupChatConsumer(BaseChatConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = None

    async def connect(self):
        await super().connect()
        self.channel = ChatGroup.channel_name(self.scope['user'].id)
        await self.channel_layer.group_add(self.channel, self.channel_name)

    async def event_group_create(self, event):
        """Функция создания группы"""
        name = event['data'].get('name')
        if not name:
            return await self._throw_error({'detail': 'Missing name room!'}, event=event['event'])
        data = await self.group_create(name, self.scope['user'])
        await self._send_message(data, event=event['event'])

    async def event_group_list(self, event):
        """Получение списка групп, в которых участвует пользователь."""
        data = await self.group_list(self.scope['user'])
        await self._send_message(data, event=event['event'])

    async def event_user_list(self, event):
        """Получения списка пользователей"""
        data = await self.user_list(self.scope['user'])
        await self._send_message(data, event=event['event'])

    @database_sync_to_async
    def group_create(self, name, user):
        """Создание объекта группы в базе данных."""
        group = ChatGroup(name=name)
        group.save()
        participant = GroupParticipant(user=user, group=group)
        participant.save()
        return {
            'id': group.id,
            'name': group.name,
            'link': group.link
        }

    @database_sync_to_async
    def group_list(self, user):
        """Получение списка групп из базы данных."""
        group_ids = list(GroupParticipant.objects.filter(user=user).values_list('group', flat=True))
        result = []
        for group in ChatGroup.objects.filter(id__in=group_ids):
            result.append({
                'id': group.id,
                'name': group.name,
                'link': group.link
            })
        return result

    @database_sync_to_async
    def user_list(self, user):
        """Получение списка пользователей из базы данных."""
        users = User.objects.all().exclude(pk=user.id)
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return result
