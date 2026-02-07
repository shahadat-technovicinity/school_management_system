from rest_framework import generics, permissions
from .models import *
from .serializers import *

class DiaryListCreateView(generics.ListCreateAPIView):
    serializer_class = TeacherDiarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TeacherDiary.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class DiaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeacherDiarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TeacherDiary.objects.filter(teacher=self.request.user)