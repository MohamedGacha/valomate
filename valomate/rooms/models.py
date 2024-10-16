from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError

class Chat(models.Model):
    members = models.ManyToManyField(get_user_model(), related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Chat between: {', '.join([user.email for user in self.members.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), related_name='message_sender')
    sent_at = models.DateTimeField(auto_now_add=True) 
    message = models.CharField(max_length=500)

    def __str__(self):
        return f"Message : {self.message}"
    
class Room(models.Model):
    description = models.CharField(max_length=500)
    leader = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='leader_rooms')
    valorant_code = models.CharField(max_length=20)
    ready = models.BooleanField(default=False)
    members = models.ManyToManyField(get_user_model(), related_name="room_members")
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="linked_chat")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.description} - Leader: {self.leader.email}"

class RoomDuo(Room):
    class Meta:
        verbose_name = "Duo Room"
        verbose_name_plural = "Duo Rooms"

    def clean(self):
        # Ensure the room has exactly 2 members
        if self.members.count() != 2:
            raise ValidationError("A Duo room must have exactly 2 members.")

class RoomTrio(Room):
    class Meta:
        verbose_name = "Trio Room"
        verbose_name_plural = "Trio Rooms"

    def clean(self):
        # Ensure the room has exactly 3 members
        if self.members.count() != 3:
            raise ValidationError("A Trio room must have exactly 3 members.")

class Room5Stack(Room):
    class Meta:
        verbose_name = "5-Stack Room"
        verbose_name_plural = "5-Stack Rooms"

    def clean(self):
        # Ensure the room has exactly 5 members
        if self.members.count() != 5:
            raise ValidationError("A 5-Stack room must have exactly 5 members.")

