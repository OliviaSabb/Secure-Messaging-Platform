from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

try:
    from .local_settings import *
except ImportError:
    pass