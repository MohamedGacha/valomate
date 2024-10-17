from django.db import models
from django.conf import settings
from django.forms import ValidationError

class Chat(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Chat between: {', '.join([user.email for user in self.members.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='message_sender', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True) 
    message = models.CharField(max_length=500)

    def __str__(self):
        return f"Message : {self.message}"
    
class Room(models.Model):
    description = models.CharField(max_length=500)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leader_rooms')
    valorant_code = models.CharField(max_length=20)
    ready = models.BooleanField(default=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="room_members")
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
        if self.members.count() > 2:
            raise ValidationError("A Duo room must have 2 members.")

class RoomTrio(Room):
    class Meta:
        verbose_name = "Trio Room"
        verbose_name_plural = "Trio Rooms"

    def clean(self):
        # Ensure the room has exactly 3 members
        if self.members.count() > 3:
            raise ValidationError("A Trio room must have 3 members.")

class Room5Stack(Room):
    class Meta:
        verbose_name = "5-Stack Room"
        verbose_name_plural = "5-Stack Rooms"

    def clean(self):
        # Ensure the room has exactly 5 members
        if self.members.count() > 5:
            raise ValidationError("A 5-Stack room must have 5 members.")

class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='request_sender', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Join request"
        verbose_name_plural = "Join requests"
        unique_together = ('sender', 'room')

    def accept(self):
        """Accept the request and add the sender to the room's members."""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()

            # Add the sender to the room's members
            if self.room.members.count() < self.get_room_capacity():
                self.room.members.add(self.sender)

                # Delete all other pending requests from this sender
                JoinRequest.objects.filter(sender=self.sender, status='pending').delete()
            else:
                raise ValidationError(f"This room is full. Maximum {self.get_room_capacity()} members allowed.")
    
    def reject(self):
        """Reject the request."""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()

    def get_room_capacity(self):
        """Return the capacity of the room based on the type."""
        if isinstance(self.room, RoomDuo):
            return 2
        elif isinstance(self.room, RoomTrio):
            return 3
        elif isinstance(self.room, Room5Stack):
            return 5
        return None

    def __str__(self):
        return f"{self.sender} requested to join {self.room} on {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"