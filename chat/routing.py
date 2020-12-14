from django.urls import re_path

from .consumers import BaseChatConsumer, GroupChatConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/groups/$', GroupChatConsumer),
    re_path(r'^ws/chat/(?P<group_id>\d+)/$', ChatConsumer),
]
