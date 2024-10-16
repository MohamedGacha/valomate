from .serializers import RoomDuoCreateSerializer, RoomTrioCreateSerializer, Room5StackCreateSerializer
from rest_framework import generics
from .models import RoomDuo, RoomTrio, Room5Stack
from valorantProfile.permissions import HasCompleteUserAgent
from rest_framework.permissions import IsAuthenticated
from .permissions import NotIsUserInAnyRoom

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


