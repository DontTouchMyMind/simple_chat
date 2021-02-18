from channels.db import database_sync_to_async

from chat.consumers import BaseChatConsumer
from chat.models import ChatGroup, GroupParticipant, User, ChatMessage


class ChatConsumer(BaseChatConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group = None
        self.participants = []
        self.channel = f'group_{self.group_id}'

    async def connect(self):
        await super().connect()
        group = await self.get_group()
        if not group:
            await self._throw_error({'detail': 'Group not found!'})
            await self.close()
            return
        await self.channel_layer.group_add(self.channel, self.channel_name)
        participants = await self.get_participants()
        if self.scope['user'].id not in participants:
            await self._throw_error({'detail': 'Access denied!'})
            await self.close()
            return
        await self.channel_layer.group_add(self.channel, self.channel_name)

    async def event_add_participant(self, event):
        """Обработчик добавления пользователя в группу."""
        user_id = event['data'].get('user_id')
        if not user_id:
            return await self._throw_error({'detail': 'Missing user id!'}, event=event['event'])
        await self.add_participant(user_id)
        participants = await self.get_participants()
        return await self._send_message(participants, event=event['event'])

    async def event_send_message(self, event):
        """Обработчик отправки сообщения в группу."""
        message = event['data'].get('message')
        if not message:
            return await self._throw_error({'detail': 'Missing message!'}, event=event['event'])
        await self.save_message(message, self.scope['user'])
        data = {
            'username': self.scope['user'].username,
            'message': event['data']['message'],
        }
        return await self._group_send(data, event=event['event'])

    async def event_list_messages(self, event):
        """Обработчик, который выводит все сообщения группы пользователю."""
        messages = await self.get_messages()
        return await self._send_message(messages, event=event['event'])

    async def event_fetch_messages(self, event):
        """Обработчик, который выводит последние 10 сообщений группы пользователю."""
        messages = await self.get_last_messages()
        return await self._send_message(messages, event=event['event'])

    @database_sync_to_async
    def get_group(self):
        """ Получаем группу, к которой присоединяется пользователь.
        Если группы не существует, то вернется None, объявленный в конструкторе."""
        group = ChatGroup.objects.filter(pk=self.group_id).first()
        if group:
            self.group = group
        return group

    @database_sync_to_async
    def get_participants(self):
        """Получаем список пользователей группы."""
        participants = list(GroupParticipant.objects.filter(group=self.group).values_list('user', flat=True))
        self.participants = participants
        return participants

    @database_sync_to_async
    def add_participant(self, user_id):
        """Добавляем пользователя в БД,в модель с ссылкой на группу, в которую его добавили."""
        user = User.objects.filter(pk=user_id).first()
        if user:
            participant, _ = GroupParticipant.objects.get_or_create(group=self.group, user=user)

    @database_sync_to_async
    def save_message(self, message, user):
        """Сохранение нового сообщения в БД."""
        new_message = ChatMessage(user=user, group=self.group, message=message)
        new_message.save()

    @database_sync_to_async
    def get_messages(self):
        """Получаем все сообщения группы."""
        messages = ChatMessage.objects.select_related('user').filter(group=self.group).order_by('id')
        result = []
        for message in messages:
            result.append({
                'id': message.id,
                'username': message.user.username,
                'message': message.message,
            })
        return result

    @database_sync_to_async
    def get_last_messages(self):
        """Получаем последние 10 сообщений группы."""
        messages = ChatMessage.objects.select_related('user').filter(group=self.group).order_by('-id')[:10:-1]
        result = []
        for message in messages:
            result.append({
                'id': message.id,
                'username': message.user.username,
                'message': message.message,
            })
        return result
