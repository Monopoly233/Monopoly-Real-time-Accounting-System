# myapp/routing.py
from django.urls import re_path
from myapp.consumers import PlayerPoolConsumer

websocket_urlpatterns = [
    re_path(r'ws/player_pool/', PlayerPoolConsumer.as_asgi()),
]
