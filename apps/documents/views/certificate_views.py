from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models.certificates import CertificateApplication, DocumentStatus
from .serializers.certificate_serializers import CertificateApplicationSerializer

class CertificateApplicationViewSet(viewsets.ModelViewSet):
    queryset = CertificateApplication.objects.all().select_related('student', 'reviewed_by').prefetch_related('attachments')
    serializer_class = CertificateApplicationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_no', 'certificate_type']

    def perform_create(self, serializer):
        # Initial timeline entry
        timeline = [{
            "status": "Application Submitted",
            "date": timezone.now().isoformat(),
            "note": "Initial application submitted by student/clerk"
        }]
        serializer.save(timeline_data=timeline)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        application = self.get_object()
        application.status = DocumentStatus.APPROVED
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        
        # Update timeline
        current_timeline = application.timeline_data or []
        current_timeline.append({
            "status": "Approved",
            "date": timezone.now().isoformat(),
            "note": request.data.get('note', 'Application approved by administrator')
        })
        application.timeline_data = current_timeline
        application.save()
        
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        application = self.get_object()
        application.status = DocumentStatus.DENIED
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        
        # Update timeline
        current_timeline = application.timeline_data or []
        current_timeline.append({
            "status": "Denied",
            "date": timezone.now().isoformat(),
            "note": request.data.get('note', 'Application denied')
        })
        application.timeline_data = current_timeline
        application.save()
        
        return Response({'status': 'denied'})

    @action(detail=True, methods=['get'])
    def preview_tc(self, request, pk=None):
        """
        Logic for PDF generation/Preview as seen in the screenshot.
        """
        application = self.get_object()
        # Here we would call a service to generate PDF template data
        return Response({
            "school_name": "HARIKHALI HIGH SCHOOL",
            "student_name": application.student.get_full_name(),
            "father_name": application.student.guardian_info.father_name if hasattr(application.student, 'guardian_info') else "N/A",
            "issue_date": timezone.now().date(),
            "template": "leaving_certificate_v1"
        })
