# myapp/routing.py

from django.urls import re_path
from . import consumers
from .consumers import PlayerPoolConsumer

websocket_urlpatterns = [
    #re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/player_pool/$', PlayerPoolConsumer.as_asgi()),
]
