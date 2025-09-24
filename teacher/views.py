from rest_framework import viewsets, filters
from .models import Teacher
from .serializers import TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "teacher_id", "first_name", "last_name", "email", "subject",
        "class_assigned", "primary_contact_number",
    ]
    ordering_fields = ["first_name", "last_name", "teacher_id", "created_at"]
    ordering = ["-created_at"]
