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
    
class UserAgent(models.Model):
    """
    Class that handles the relationship between users and their preferred agents in Valorant.
    A user can select one agent as their main agent.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="user_agents")
    
    # Add constraints to prevent the same user from selecting the same agent multiple times
    class Meta:
        unique_together = ('user', 'agent')
        verbose_name = "User Agent"
        verbose_name_plural = "User Agents"

    def __str__(self):
        return f"{self.user} - {self.agent} - {self.agent.category}"