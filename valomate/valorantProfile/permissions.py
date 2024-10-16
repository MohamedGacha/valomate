from rest_framework.permissions import BasePermission
from .models import UserAgent

class HasCompleteUserAgent(BasePermission):
    """
    Custom permission to check if the user has completed all required fields in their UserAgent profile.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        try:
            # Fetch the UserAgent for the authenticated user
            user_agent = UserAgent.objects.get(user=request.user)

            # Check if all required fields are filled in
            fields_to_check = [user_agent.riot_id, user_agent.region, user_agent.agent, user_agent.platform, user_agent.play_style]

            # If any of these fields are empty or None, deny access
            if all(fields_to_check):
                return True
            else:
                return False
        except UserAgent.DoesNotExist:
            # If the user does not have a UserAgent profile, deny access
            return False
