from rest_framework import viewsets, permissions
from ..models.results import StudentResult
from ..serializers.results import StudentResultSerializer

class StudentResultViewSet(viewsets.ModelViewSet):
    queryset = StudentResult.objects.all()
    serializer_class = StudentResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
