from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^register/$', views.UserRegister.as_view(), name='register'),
    url(r'^login/$', views.UserLogin.as_view(), name='login'),
    url(r'^logout/$', views.UserLogout.as_view(), name='logout'),
    url(r'^me/$', views.UserMe.as_view(), name='me'),
    url(r'^me/games/$', views.UserMeGames.as_view(), name='me_games'),
    url(r'^me/games/finished/$', views.UserMeFinishedGames.as_view(), name='me_finished_games'),
    url(r'^(?P<pk>[\d-]+)$', views.UserInfo.as_view(), name='user_info'),
]
