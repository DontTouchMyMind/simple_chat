from django.urls import re_path

from .consumers import BaseChatConsumer, GroupChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/groups/$', GroupChatConsumer),
]
