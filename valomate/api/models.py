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

class Agent(models.Model):
    # Defining the categories and assigning agents to each category
    CONTROLLERS = ['Brimstone', 'Viper', 'Omen', 'Astra', 'Harbor', 'Clove']
    SENTINELS = ['Sage', 'Cypher', 'Killjoy', 'Chamber', 'Deadlock', 'Vyse']
    DUALISTS = ['Phoenix', 'Reyna', 'Jett', 'Raze', 'Yoru', 'Neon', 'Iso']
    INITIATORS = ['Sova', 'Breach', 'Skye', 'KAY/O', 'Fade', 'Gekko']

    AGENT_CHOICES = CONTROLLERS + SENTINELS + DUALISTS + INITIATORS

    # Defining the category choices
    CATEGORY_CHOICES = [
        ('Controller', 'Controller'),
        ('Sentinel', 'Sentinel'),
        ('Duelist', 'Duelist'),
        ('Initiator', 'Initiator'),
    ]

    # Fields for the Agent model
    name = models.CharField(max_length=50, choices=[(agent, agent) for agent in AGENT_CHOICES], unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Ensure the agent is in the correct category before saving
        if self.name in self.CONTROLLERS:
            self.category = 'Controller'
        elif self.name in self.SENTINELS:
            self.category = 'Sentinel'
        elif self.name in self.DUALISTS:
            self.category = 'Duelist'
        elif self.name in self.INITIATORS:
            self.category = 'Initiator'
        else:
            raise ValueError("Invalid agent name.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name