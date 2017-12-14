from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    won = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    won_by_surrender = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    surrendered = models.IntegerField(default=0)
