from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.admissions.models import StudentAdmission
from apps.admissions.serializers.completion_serializers import (
    CompletedAdmissionSerializer,
)
from apps.admissions.services.enrollment_service import finalize_admission


class AdmissionCompletionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides selected (not-yet-enrolled) applicants and an endpoint to
    finalize their enrollment, which consumes one seat.
    """
    serializer_class = CompletedAdmissionSerializer

    def get_queryset(self):
        return StudentAdmission.objects.filter(
            admission_status='selected'
        ).prefetch_related('skills__skill', 'previous_academic_record')

    @swagger_auto_schema(
        parser_classes=[MultiPartParser, FormParser],
        manual_parameters=[
            openapi.Parameter(
                'tc', openapi.IN_FORM, description="Transfer Certificate (file)",
                type=openapi.TYPE_FILE, required=False,
            ),
            openapi.Parameter(
                'mother_nid', openapi.IN_FORM, description="Mother NID (file)",
                type=openapi.TYPE_FILE, required=False,
            ),
            openapi.Parameter(
                'birth_certificate', openapi.IN_FORM,
                description="Birth Certificate (file)",
                type=openapi.TYPE_FILE, required=False,
            ),
            openapi.Parameter(
                'student_photo', openapi.IN_FORM, description="Student Photo (file)",
                type=openapi.TYPE_FILE, required=False,
            ),
        ],
        responses={
            201: openapi.Response("Admission completed", CompletedAdmissionSerializer),
            400: "No documents / not selectable",
        },
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def finalize(self, request, pk=None):
        uploaded_files = request.FILES.dict()

        if not uploaded_files:
            return Response(
                {"error": "No documents provided (Requires TC / NID / Photo)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile = finalize_admission(self.get_object().id, uploaded_files)
            serializer = CompletedAdmissionSerializer(
                self.get_object(), context={'request': request}
            )
            return Response(
                {
                    "message": "Admission Completed Successfully. Student Profile Generated.",
                    "student_id": profile.admission_number,
                    "admission": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "System Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )