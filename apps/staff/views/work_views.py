from rest_framework import viewsets
from ..models import WorkAssignment
from ..serializers.work_serializers import WorkAssignmentSerializer

class WorkAssignmentViewSet(viewsets.ModelViewSet):
    queryset = WorkAssignment.objects.all()
    serializer_class = WorkAssignmentSerializer
