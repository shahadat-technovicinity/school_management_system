from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.admissions.models import StudentAdmission
from apps.admissions.serializers.form_serializers import StudentAdmissionSerializer

class AdmissionFormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling New Student Admission Form (Create) and Forms Management (List/Patch)
    """
    queryset = StudentAdmission.objects.all().order_by('-admission_date') # Using default sorting or ordering
    serializer_class = StudentAdmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # Query parameters filter fields
    filterset_fields = ['admission_status', 'desired_class', 'payment_status']
    search_fields = ['student_name_english', 'application_number', 'mobile_number']
    
    def get_queryset(self):
        # Override to enable dynamic optimization (e.g. prefetch related data)
        return StudentAdmission.objects.prefetch_related('skills__skill', 'previous_academic_record').all()

    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """
        API for quickly updating the application status
        """
        admission = self.get_object()
        new_status = request.data.get('status')
        if new_status in [choice[0] for choice in StudentAdmission.ADMISSION_STATUS_CHOICES]:
            admission.admission_status = new_status
            admission.save()
            return Response({'message': f'Status updated to {new_status}'})
        return Response({'error': 'Invalid status provided'}, status=status.HTTP_400_BAD_REQUEST)