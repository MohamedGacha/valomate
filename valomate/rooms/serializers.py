from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Room, RoomDuo, RoomTrio, Room5Stack, Chat

class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['description', 'valorant_code']  # Exclude 'ready' from input

    def create(self, validated_data):
        """
        Custom create method to set the leader, create chat, and add the leader as a member.
        Room is created with 'ready=False' by default.
        """
        # Set the leader as the current user (request user)
        user = self.context['request'].user
        
        # Create a new Chat instance for this room
        chat = Chat.objects.create()
        
        # Force 'ready=False' and create the room with the leader and the chat
        room = Room.objects.create(
            leader=user,
            chat=chat,
            ready=False,  # Enforce ready to be False on creation
            **validated_data
        )
        
        # Automatically set the leader as the only member initially
        room.members.set([user])
        
        return room

class RoomDuoCreateSerializer(RoomCreateSerializer):
    class Meta(RoomCreateSerializer.Meta):
        model = RoomDuo
        fields = RoomCreateSerializer.Meta.fields

    def create(self, validated_data):
        # Call the parent create method to handle common behavior
        room = super().create(validated_data)
        return room

class RoomTrioCreateSerializer(RoomCreateSerializer):
    class Meta(RoomCreateSerializer.Meta):
        model = RoomTrio
        fields = RoomCreateSerializer.Meta.fields

    def create(self, validated_data):
        # Call the parent create method to handle common behavior
        room = super().create(validated_data)
        return room

class Room5StackCreateSerializer(RoomCreateSerializer):
    class Meta(RoomCreateSerializer.Meta):
        model = Room5Stack
        fields = RoomCreateSerializer.Meta.fields

    def create(self, validated_data):
        # Call the parent create method to handle common behavior
        room = super().create(validated_data)
        return room
