from django.db import models
from django.contrib.auth.models import AbstractUser

STATUS_CHOICES = [
    ('a', 'Active user'),
    ('b', 'Banned user'),
]


class User(AbstractUser):
    user_status = models.CharField(max_length=1, default='a', choices=STATUS_CHOICES)
    user_information = models.TextField(max_length=500, blank=True)
