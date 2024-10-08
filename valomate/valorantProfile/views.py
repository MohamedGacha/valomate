from rest_framework import generics
from .models import Agent, Platform, Rank, UserAgent
from rest_framework.response import Response
from .serializers import RankSerializer, UserAgentBulkUpdateSerializer, UserAgentPlatformUpdateSerializer, UserAgentSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class SelectAgentsView(generics.CreateAPIView):
    serializer_class = UserAgentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 

    def get_queryset(self):
        return UserAgent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UpdateUserAgentPlatformView(generics.UpdateAPIView):
    queryset = UserAgent.objects.all()
    serializer_class = UserAgentPlatformUpdateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Filter to ensure users can only update their own records
        return UserAgent.objects.filter(user=self.request.user)
    
class UserAgentListUpdateView(generics.GenericAPIView):
    serializer_class = UserAgentBulkUpdateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Agent list updated successfully!"})
    
class PlatformUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        platform_name = request.data.get('platform')

        # Validate platform existence
        try:
            platform = Platform.objects.get(platform=platform_name.upper())
        except Platform.DoesNotExist:
            return Response({"error": "Invalid platform name."}, status=400)

        # Update platform for all UserAgent records of the user
        UserAgent.objects.filter(user=user).update(platform=platform)
        return Response({"message": "Platform updated successfully!"})
    
class UserAgentRankSelectView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = RankSerializer  # Use a serializer for the Rank model

    def get_queryset(self):
        # Retrieve UserAgent instances related to the authenticated user
        return UserAgent.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        user_agent = self.get_queryset().first()  # Assuming one user agent per user
        if not user_agent:
            return Response({"error": "UserAgent not found."}, status=404)

        # Validate and update the rank name
        rank_name = request.data.get('rank')
        if not rank_name:
            return Response({"error": "Rank name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the Rank instance by its name
        try:
            rank = Rank.objects.get(rank=rank_name)
        except Rank.DoesNotExist:
            return Response({"error": "Rank not found."}, status=404)

        user_agent.rank = rank
        user_agent.save()  # Save the updated user agent

        return Response({"message": "Rank updated successfully!", "rank": str(rank)}, status=200)

class UserRankUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Retrieve UserAgent instances related to the authenticated user
        return UserAgent.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        # Get the user agent for the authenticated user
        user_agent = self.get_queryset().first()  # Assuming one user agent per user
        if user_agent is None:
            return Response({"error": "UserAgent not found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the rank name from the request data
        rank_name = request.data.get('rank')
        if not rank_name:
            return Response({"error": "Rank name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the Rank instance by its name
        rank_instance = Rank.objects.filter(rank=rank_name).first()
        if rank_instance is None:
            return Response({"error": "Rank not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the rank of the UserAgent
        user_agent.rank = rank_instance
        user_agent.save()

        return Response({"message": "Rank updated successfully!", "rank": user_agent.rank.rank})

class UpdateUserAgentRegionView(generics.UpdateAPIView):
    """
    View to update the region of a UserAgent for the authenticated user.
    """
    serializer_class = UserAgentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Filter to ensure users can only update their own UserAgent records
        return UserAgent.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        user_agent = self.get_queryset().first()  # Assuming one user agent per user
        if not user_agent:
            return Response({"error": "UserAgent not found."}, status=404)

        # Update the region of the UserAgent
        region_id = request.data.get('region')  # Assuming the region ID is sent in the request
        if not region_id:
            return Response({"error": "Region ID is required."}, status=400)

        # Validate and update the region
        try:
            user_agent.region_id = region_id  # Set the new region
            user_agent.save()  # Save the changes
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Region updated successfully!", "region": str(user_agent.region)}, status=200)
    
class SetValorantProfileView(generics.CreateAPIView):
    """
    API view to allow users to set up their Valorant profile (including riot_id, region, agent, platform, play_style, and rank).
    """
    serializer_class = UserAgentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return UserAgent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user automatically for the UserAgent object
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # Custom handling of the POST request for creating a Valorant profile
        data = request.data

        agent_name = data.get('agent')
        platform_name = data.get('platform')
        rank_name = data.get('rank')

        # Validate agent
        try:
            agent = Agent.objects.get(name=agent_name)
        except Agent.DoesNotExist:
            return Response({'error': 'Agent does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate platform
        try:
            platform = Platform.objects.get(platform=platform_name.upper())
        except Platform.DoesNotExist:
            return Response({'error': 'Platform does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate rank (if provided)
        rank = None
        if rank_name:
            try:
                rank = Rank.objects.get(rank=rank_name)
            except Rank.DoesNotExist:
                return Response({'error': 'Rank does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # All validations passed, save the profile
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, agent=agent, platform=platform, rank=rank)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ValorantMeView(generics.RetrieveAPIView):
    """
    API view to retrieve the current logged-in user's Valorant profile (UserAgent) data.
    """
    serializer_class = UserAgentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Ensure only the logged-in user's UserAgent data is returned
        return UserAgent.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Retrieve the first UserAgent object for the logged-in user
        user_agent = self.get_queryset().first()
        if not user_agent:
            return Response({"error": "No Valorant profile found for this user."}, status=404)

        serializer = self.get_serializer(user_agent)
        return Response(serializer.data)