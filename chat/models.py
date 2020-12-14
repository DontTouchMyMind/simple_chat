from django.db import models
from django.contrib.auth.models import AbstractUser

STATUS_CHOICES = [
    ('a', 'Active user'),
    ('b', 'Banned user'),
]


class User(AbstractUser):
    user_status = models.CharField(max_length=1, default='a', choices=STATUS_CHOICES)
    user_information = models.TextField(max_length=500, blank=True)


class ChatGroup(models.Model):
    """Модель группы"""
    name = models.CharField(max_length=255, default='')

    @property
    def link(self):
        channel_name = self.channel_name(self.id)
        return f'/ws/chat/{self.id}'

    def __str__(self):
        return self.name

    @classmethod
    def channel_name(cls, group_id):
        return f'group_{group_id}'

    @classmethod
    def user_channel_name(cls, user_id):
        return f'user_{user_id}'


class GroupParticipant(models.Model):
    """Модель, которая хранит пользователя и ссылку на группу в которой он состоит."""
    user = models.ForeignKey(User, related_name='group_user', on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(ChatGroup, related_name='group_participant', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username


class ChatMessage(models.Model):
    """Модель сообщения, которая хранит данные о том, кто создатель сообщения в какую группу оно отправлено."""
    user = models.ForeignKey(User, related_name='user_message', on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(ChatGroup, related_name='group_message', on_delete=models.CASCADE, null=True)
    message = models.TextField(default='')

    def __str__(self):
        return self.message
