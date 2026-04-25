from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.students.models import Student
from apps.students.serializers.management_serializers import StudentManagementSerializer
from apps.students.services.enrollment_service import EnrollmentService

class StudentManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Student Grid/List view and adding new students.
    Matches the "All Students" and "Add Student" UI screens.
    """
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentManagementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering options for the UI
    filterset_fields = ['status', 'academic_year', 'gender', 'blood_group']
    search_fields = ['first_name', 'last_name', 'admission_number', 'roll_number', 'primary_contact_number']
    ordering_fields = ['created_at', 'admission_date', 'first_name']

    def create(self, request, *args, **kwargs):
        # We can use the service layer here if needs extra non-DRF validation
        # But for now, standard DRF serializer.save() (which handles nested models) is used.
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Use service to get the "360 degree" profile if requested
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Example: Injecting extra profile data from other apps eventually
        data = serializer.data
        # data['extra_profile_stats'] = EnrollmentService.get_student_360_profile(instance.id)
        
        return Response(data)
