from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.admissions.models import StudentAdmission
from apps.admissions.serializers.form_serializers import StudentAdmissionSerializer
from apps.admissions.services.enrollment_service import finalize_admission

class AdmissionCompletionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides pending/selected applicants list and endpoint to finalize documents
    """
    serializer_class = StudentAdmissionSerializer

    def get_queryset(self):
        # We only show users who are "Selected" but not yet "Enrolled"
        return StudentAdmission.objects.filter(admission_status='selected').prefetch_related('skills__skill', 'previous_academic_record')

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """
        Takes uploaded files and triggers the enrollment service
        """
        uploaded_files = request.FILES.dict()
        
        if not uploaded_files:
            return Response({"error": "No documents provided (Requires TC / NID / Photo)"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Service does heavy lifting to extract documents and map Profile data
            profile = finalize_admission(self.get_object().id, uploaded_files)
            
            return Response({
                "message": "Admission Completed Successfully. Student Profile Generated.",
                "student_id": profile.admission_number
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "System Error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
