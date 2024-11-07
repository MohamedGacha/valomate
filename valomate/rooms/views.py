from .serializers import JoinRequestSerializer, RoomDuoCreateSerializer, RoomTrioCreateSerializer, Room5StackCreateSerializer, JoinRequest, ChatSerializer, MessageSerializer
from rest_framework import generics
from .models import Chat, Room, RoomDuo, RoomTrio, Room5Stack, Message
from valorantProfile.permissions import HasCompleteUserAgent
from rest_framework.permissions import IsAuthenticated
from .permissions import NotIsUserInAnyRoom
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from itertools import chain

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
    permission_classes = [IsAuthenticated]
    def get_queryset(self, request, *args, **kwargs):
        return JoinRequest.objects.filter(room__leader=request.user)

    def put(self, request, *args, **kwargs):
        join_request = self.get_object()

        # Check if the requester is the room leader
        if join_request.room.leader != request.user:
            return Response({'error': 'Only the room leader can reject join requests.'}, status=status.HTTP_403_FORBIDDEN)

        join_request.reject()  # Reject the request
        return Response({'message': 'Join request rejected.'}, status=status.HTTP_200_OK)
    
class GetRoomsWithFilters(APIView):
    permission_classes = [IsAuthenticated, NotIsUserInAnyRoom]
    def get_queryset(self):
        # Get all RoomDuo, RoomTrio, and Room5Stack instances
        duos = RoomDuo.objects.all()
        trios = RoomTrio.objects.all()
        stacks = Room5Stack.objects.all()

        return duos, trios, stacks
    
    def get(self, request, *args, **kwargs):

        duo = request.query_params.get('duo') == 'true'
        trio = request.query_params.get('trio') == 'true'
        stack = request.query_params.get('stack') == 'true'
        one_to_go = request.query_params.get('last') == 'true'

        # Get the corresponding room types
        duos, trios, stacks = self.get_queryset()

        # Initialize the list to hold the final rooms
        final_rooms = []

        # Filter and append based on query params
        if duo:
            final_rooms.extend(duos)
        if trio:
            final_rooms.extend(trios)
        if stack:
            final_rooms.extend(stacks)


        # If 'one_to_go' is True, filter rooms that need only one more member to be full
        if one_to_go:
            final_rooms = [room for room in final_rooms if self.needs_one_more_member(room)]

        # Sort rooms by number of members in descending order
        sorted_rooms = sorted(
            final_rooms,
            key=lambda room: room.members.count(),  # Sort by the number of members
            reverse=True  # Descending order
        )

        # Return the list of rooms in the response, sorted by number of members
        return Response({"rooms": [room.id for room in sorted_rooms]})

    
    def needs_one_more_member(self, room):
        """Check if the room needs one more member to be full."""
        # Get the number of members in the room
        num_members = room.members.count()

        if isinstance(room, RoomDuo):
            return num_members == 1  # Duo room needs 1 member
        elif isinstance(room, RoomTrio):
            return num_members == 2  # Trio room needs 2 members
        elif isinstance(room, Room5Stack):
            return num_members == 4  # 5-Stack room needs 4 members
        return False
    
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter messages by chat ID, passed as a URL parameter
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        # Automatically set the sender as the logged-in user
        serializer.save(sender=self.request.user)

class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        # Check if the sender is a member of the chat
        if self.request.user not in chat.members.all():
            raise PermissionDenied("You are not a member of this chat.")

        # Save the message with the sender and chat
        serializer.save(sender=self.request.user, chat=chat)