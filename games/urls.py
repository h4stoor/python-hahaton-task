from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.GameRecent.as_view(), name='game_list'),
    url(r'^(?P<pk>[\d-]+)/moves/$', views.GameMoves.as_view(), name='game_moves'),
    url(r'^(?P<pk>[\d-]+)/moves/last/$', views.GameLastMove.as_view(), name='game_last_move'),
    url(r'^(?P<pk>[\d-]+)/(?P<action>[\w]+)/$', views.GameAction.as_view(), name='game_action'),
    url(r'^(?P<pk>[\d-]+)$', views.GameDetail.as_view(), name='game_detail'),
]
