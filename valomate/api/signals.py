from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import EmailVerification
from django.utils.crypto import get_random_string

@receiver(post_save, sender=User)
def create_email_verification(sender, instance, created, **kwargs):
    if created:
        token = get_random_string(length=32)
        EmailVerification.objects.create(user=instance, token=token)
