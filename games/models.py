from django.db import models
from django.conf import settings

from jsonfield import JSONField

from .const import EMPTY_BOARD


class Game(models.Model):
    board = JSONField(default=EMPTY_BOARD)
    
    players_count = models.IntegerField(default=1)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    surrendered = models.BooleanField(default=False)
    draw = models.BooleanField(default=False)
    
    now_turn = models.IntegerField(default=-1)


class Player(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    game = models.ForeignKey(Game, default=False)
    
    won = models.BooleanField(default=False)
    owner = models.BooleanField(default=False)
    first = models.BooleanField(default=False)


class Move(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    
    timestamp = models.DateTimeField(auto_now=True)
    x = models.IntegerField()
    y = models.IntegerField()
    
    class Meta:
        ordering = ('-timestamp',)
