from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.admissions.models import StudentAdmission
from apps.admissions.serializers.form_serializers import StudentAdmissionSerializer,ChangeStatusSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.common.pagination.standard_pagination import StandardPagination

class AdmissionFormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling New Student Admission Form (Create) and Forms Management (List/Patch)

    List Query Parameters:
        admission_status (str): Filter by admission status (pending, interview, selected, rejected, enrolled)
        payment_status (str): Filter by payment status (pending, paid, failed)
        desired_class (str): Filter by desired class
        search (str): Search by student name, application number, or mobile number
    """
    queryset = StudentAdmission.objects.all().order_by('-admission_date') # Using default sorting or ordering
    serializer_class = StudentAdmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = StandardPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    # Query parameters filter fields
    filterset_fields = ['admission_status', 'desired_class', 'payment_status']
    search_fields = ['student_name_english', 'application_number', 'mobile_number']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'admission_status',
                openapi.IN_QUERY,
                description="Filter by admission status",
                type=openapi.TYPE_STRING,
                enum=['pending', 'interview', 'selected', 'rejected', 'enrolled'],
                required=False,
            ),
            openapi.Parameter(
                'payment_status',
                openapi.IN_QUERY,
                description="Filter by payment status",
                type=openapi.TYPE_STRING,
                enum=['pending', 'paid', 'failed'],
                required=False,
            ),
            openapi.Parameter(
                'desired_class',
                openapi.IN_QUERY,
                description="Filter by desired class",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search by student name (English), application number, or mobile number",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        # Override to enable dynamic optimization (e.g. prefetch related data)
        return StudentAdmission.objects.prefetch_related('skills__skill', 'previous_academic_record').all()

    @swagger_auto_schema(
        request_body=ChangeStatusSerializer,
        responses={
            200: openapi.Response("Status updated", ChangeStatusSerializer),
            400: "Invalid status provided",
        },
    )
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """
        API for manually updating the application status to any valid value.
        """
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admission = self.get_object()
        admission.admission_status = serializer.validated_data['status']
        admission.save()
        return Response({
            'message': f'Status updated to {admission.admission_status}',
            'status': admission.admission_status,
        })