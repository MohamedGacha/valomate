from django.urls import path
from .views import (
    CreateRoomDuoView,
    CreateRoomTrioView,
    CreateRoom5StackView,
    CreateJoinRequestView,
    AcceptJoinRequestView,
    RejectJoinRequestView,
)

urlpatterns = [
    path('create/room/duo/', CreateRoomDuoView.as_view(), name='create_duo_room'),
    path('create/room/trio/', CreateRoomTrioView.as_view(), name='create_trio_room'),
    path('create/room/5stack/', CreateRoom5StackView.as_view(), name='create_5stack_room'),
    path('room/<int:room_id>/join/', CreateJoinRequestView.as_view(), name='join-room-request'),
    path('room/<int:room_id>/join-requests/<int:request_id>/accept/', AcceptJoinRequestView.as_view(), name='accept_join_request'),
    path('room/<int:room_id>/join-requests/<int:request_id>/reject/', RejectJoinRequestView.as_view(), name='reject_join_request'),
]
