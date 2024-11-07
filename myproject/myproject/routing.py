# myproject/routing.py
from django.urls import re_path
from myapp.consumers import PlayerPoolConsumer  # 导入你的 WebSocket 消费者

websocket_urlpatterns = [
    re_path(r'ws/player_pool/$', PlayerPoolConsumer.as_asgi()),  # 配置 WebSocket 路由
]
