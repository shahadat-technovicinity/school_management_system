from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.students.models import Student
from apps.students.serializers.management_serializers import StudentManagementSerializer


class StudentManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Student Grid/List view and adding new students.
    Matches the "All Students" and "Add Student" UI screens.
    """
    serializer_class = StudentManagementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['status', 'academic_year', 'gender', 'blood_group', 'class_name_static', 'section_static']
    search_fields = ['first_name', 'last_name', 'admission_number', 'roll_number', 'primary_contact_number']
    ordering_fields = ['created_at', 'admission_date', 'first_name']

    def get_queryset(self):
        return Student.objects.prefetch_related(
            'enrollment_set', 
            'enrollment_set__classname', 
            'enrollment_set__section'
        ).all().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)