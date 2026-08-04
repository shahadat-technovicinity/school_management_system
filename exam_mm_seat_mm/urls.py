from django.urls import path
from .views import (
    ExamRoomListCreateView, ExamRoomDetailView,
    ExamSessionListCreateView, ExamSessionDetailView,
    RoomClassAssignmentListCreateView, RoomClassAssignmentDetailView,
    SeatAssignmentListCreateView, SeatAssignmentDetailView,
    SeatsByRoomView, GenerateSeatPlanView
)

urlpatterns = [
    # path('rooms/', ExamRoomListCreateView.as_view(), name='exam-room-list'),
    # path('rooms/<int:pk>/', ExamRoomDetailView.as_view(), name='exam-room-detail'),

    # path('sessions/', ExamSessionListCreateView.as_view(), name='exam-session-list'),
    # path('sessions/<int:pk>/', ExamSessionDetailView.as_view(), name='exam-session-detail'),

    # path('class-assignments/', RoomClassAssignmentListCreateView.as_view(), name='class-assignment-list'),
    # path('class-assignments/<int:pk>/', RoomClassAssignmentDetailView.as_view(), name='class-assignment-detail'),

    # path('seats/', SeatAssignmentListCreateView.as_view(), name='seat-list'),
    # path('seats/<int:pk>/', SeatAssignmentDetailView.as_view(), name='seat-detail'),
    # path('seats/by-room/', SeatsByRoomView.as_view(), name='seats-by-room'),
    # path('seats/generate/', GenerateSeatPlanView.as_view(), name='generate-seat-plan'),
]