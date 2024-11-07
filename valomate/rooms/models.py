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

    class RoomType(models.IntegerChoices):
        DUO = 2, 'Duo'
        TRIO = 3, 'Trio'
        FIVE_STACK = 5, '5-Stack'

    description = models.CharField(max_length=500)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leader_rooms')
    valorant_code = models.CharField(max_length=20)
    ready = models.BooleanField(default=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="room_members")
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="linked_chat")
    room_type = models.IntegerField(choices=RoomType.choices)

    def kick(self, user):
        """Kick a user from the room. If the user is the leader, assign a new leader."""
        if user not in self.members.all():
            raise ValidationError("User is not a member of this room.")

        # If the user is the leader, assign a new leader from remaining members
        if user == self.leader:
            remaining_members = list(self.members.exclude(id=user.id))
            if remaining_members:
                # Choose the first member in the remaining list as the new leader
                self.leader = remaining_members[0]
                self.save()
            else:
                raise ValidationError("Cannot remove leader. Room must have at least one member to assign a new leader.")

        # Remove the user from the room's members
        self.members.remove(user)
        self.save()

        # If the room is empty after the kick, delete it
        if not self.members.exists():
            self.delete()

    def __str__(self):
        return f"{self.description} - Leader: {self.leader.username}"

class RoomDuo(Room):
    class Meta:
        verbose_name = "Duo Room"
        verbose_name_plural = "Duo Rooms"

    def clean(self):
        # Ensure the room has exactly 2 members
        if self.members.count() > 2:
            raise ValidationError("A Duo room must have 2 members.")
        # Ensure the room_type is set to DUO
        if self.room_type != Room.RoomType.DUO:
            raise ValidationError("This room should be a Duo Room.")

class RoomTrio(Room):
    class Meta:
        verbose_name = "Trio Room"
        verbose_name_plural = "Trio Rooms"

    def clean(self):
        # Ensure the room has exactly 3 members
        if self.members.count() > 3:
            raise ValidationError("A Trio room must have 3 members.")
        # Ensure the room_type is set to TRIO
        if self.room_type != Room.RoomType.TRIO:
            raise ValidationError("This room should be a Trio Room.")

class Room5Stack(Room):
    class Meta:
        verbose_name = "5-Stack Room"
        verbose_name_plural = "5-Stack Rooms"

    def clean(self):
        # Ensure the room has exactly 5 members
        if self.members.count() > 5:
            raise ValidationError("A 5-Stack room must have 5 members.")
        # Ensure the room_type is set to FIVE_STACK
        if self.room_type != Room.RoomType.FIVE_STACK:
            raise ValidationError("This room should be a 5-Stack Room.")

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

            # Check if the user is already in a room and kick them out
            current_room = self.sender.room_members.first()  # Get the first room the user is part of (if any)
            if current_room:
                current_room.kick(self.sender)  # Kick the user out of the current room
            
            # Add the sender to the new room's members
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