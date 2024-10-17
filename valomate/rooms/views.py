from .serializers import JoinRequestSerializer, RoomDuoCreateSerializer, RoomTrioCreateSerializer, Room5StackCreateSerializer, JoinRequest
from rest_framework import generics
from .models import Room, RoomDuo, RoomTrio, Room5Stack
from valorantProfile.permissions import HasCompleteUserAgent
from rest_framework.permissions import IsAuthenticated
from .permissions import NotIsUserInAnyRoom
from rest_framework.response import Response
from rest_framework import status

class CreateRoomDuoView(generics.CreateAPIView):
    queryset = RoomDuo.objects.all()
    serializer_class = RoomDuoCreateSerializer
    permission_classes = [NotIsUserInAnyRoom, HasCompleteUserAgent, IsAuthenticated] 

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(leader=user, members=[user], ready=False)

class CreateRoomTrioView(generics.CreateAPIView):
    queryset = RoomTrio.objects.all()
    serializer_class = RoomTrioCreateSerializer
    permission_classes = [NotIsUserInAnyRoom, HasCompleteUserAgent, IsAuthenticated] 

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(leader=user, members=[user], ready=False)

class CreateRoom5StackView(generics.CreateAPIView):
    queryset = Room5Stack.objects.all()
    serializer_class = Room5StackCreateSerializer
    permission_classes = [NotIsUserInAnyRoom, HasCompleteUserAgent, IsAuthenticated] 

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(leader=user, members=[user], ready=False)


class CreateJoinRequestView(generics.CreateAPIView):
    serializer_class = JoinRequestSerializer
    permission_classes = [IsAuthenticated,NotIsUserInAnyRoom, HasCompleteUserAgent]

    def post(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')  # Get room ID from the URL
        try:
            room = Room.objects.get(id=room_id)  # Ensure the room exists
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the room field and validate
        serializer = self.get_serializer(data={'room': room.id})
        serializer.is_valid(raise_exception=True)

        # Save the join request with the current user as the sender
        join_request = JoinRequest.objects.create(sender=request.user, room=room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class AcceptJoinRequestView(generics.UpdateAPIView):
    queryset = JoinRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        join_request = self.get_object()

        # Check if the requester is the room leader
        if join_request.room.leader != request.user:
            return Response({'error': 'Only the room leader can accept join requests.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            join_request.accept()  # Accept the request and add the user to the room
            return Response({'message': 'Join request accepted and user added to the room.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RejectJoinRequestView(generics.UpdateAPIView):
    queryset = JoinRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        join_request = self.get_object()

        # Check if the requester is the room leader
        if join_request.room.leader != request.user:
            return Response({'error': 'Only the room leader can reject join requests.'}, status=status.HTTP_403_FORBIDDEN)

        join_request.reject()  # Reject the request
        return Response({'message': 'Join request rejected.'}, status=status.HTTP_200_OK)