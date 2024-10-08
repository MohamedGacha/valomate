from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from uuid import uuid4
from django.utils import timezone
# Create your models here.

class EmailVerification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)

