from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
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
        return f"{self.name} - {self.category}" 
    
class Platform(models.Model):
    PLATFORM_CHOICES = [
        ('PC', 'PC'),
        ('XBOX', 'Xbox'),
        ('PLAYSTATION', 'Playstation'),
        ('MOBILE', 'Mobile'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)

    def __str__(self):
        return f"{self.platform}"
    
class UserAgent(models.Model):
    """
    Class that handles the relationship between users and their preferred agents in Valorant.
    A user can select multiple agents as their main agents, each with a unique play style.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="user_agents")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="user_platforms")
    play_style = models.CharField(max_length=500, default="", help_text="Describe your play style with this agent")

    class Meta:
        # Ensure each user-agent-play_style combination is unique
        unique_together = ('user', 'agent', 'play_style')
        verbose_name = "User Agent"
        verbose_name_plural = "User Agents"

    def __str__(self):
        return f"{self.user} - {self.agent} on {self.platform} - ({self.agent.category}) - Play Style: {self.play_style}"
