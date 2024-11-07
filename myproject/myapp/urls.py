from django.urls import reverse, path, re_path
from . import views
from .views import get_players
from django.urls import re_path
from .consumers import PlayerPoolConsumer

websocket_urlpatterns = [
    re_path(r'ws/player_pool/$', PlayerPoolConsumer.as_asgi()),
]


urlpatterns = [
    path('', views.home),
    path('sayhello/', views.sayhello),
    path('drinks/<str:drink_name>', views.drinks, name="drink_name"),
    path('menu/', views.menu, name="menu"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('api/players/', get_players, name='get_players'),
]