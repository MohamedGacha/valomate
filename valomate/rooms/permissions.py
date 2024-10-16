from rest_framework import permissions
from .models import RoomDuo, RoomTrio, Room5Stack

class NotIsUserInAnyRoom(permissions.BasePermission):
    """
    Custom permission to check if the user is already leading or part of any room.
    """

    def has_permission(self, request, view):
        # Allow unauthenticated users to access the view
        if not request.user.is_authenticated:
            return True

        # Check if the user is already leading or a member of any room
        is_in_room = (
            RoomDuo.objects.filter(leader=request.user).exists() or
            RoomTrio.objects.filter(leader=request.user).exists() or
            Room5Stack.objects.filter(leader=request.user).exists() or
            request.user.room_members.exists()
        )

        return not is_in_room  # Deny permission if user is in any room
