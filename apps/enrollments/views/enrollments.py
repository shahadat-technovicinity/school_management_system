from apps.common.pagination.standard_pagination import StandardPagination
from apps.common.views.basemodelview import BaseModelViewSet
from apps.enrollments.serializers.enrollments import EnrollmentSerializer, BulkEnrollmentSerializer
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from apps.enrollments.models import Enrollment
from apps.students.models import Student
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.academics.models import AcademicYear
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EnrollmentViewSet(BaseModelViewSet):
    """
    CRUD API for Enrollment.
    Supports filtering, search and ordering via query params.
    Example query params:
      ?student=1
      ?course=2
      ?search=john
      ?ordering=-created_at
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    # permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['student', 'course', 'status', 'term']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date']

    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        student = enrollment.student
        student.class_name_static = enrollment.classname
        student.section_static = enrollment.section
        student.save(update_fields=['class_name_static', 'section_static'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        request_body=BulkEnrollmentSerializer,
        responses={
            201: openapi.Response("Bulk enrollment created"),
            400: "Bad request - duplicate enrollment or missing students",
            404: "Students not found",
        }
    )
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        serializer = BulkEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        student_ids = data['student_ids']
        classname = data['classname']
        section = data.get('section', 'A')

        academic_year = data.get('academic_year')
        if not academic_year:
            active_year = AcademicYear.objects.filter(is_active=True).first()
            academic_year = active_year.year_label if active_year else "2025-2026"

        # Validate students exist and fetch their existing roll numbers
        students_qs = Student.objects.filter(id__in=student_ids).only('id', 'roll_number')
        existing_students = {s.id: s for s in students_qs}
        missing_ids = set(student_ids) - set(existing_students.keys())
        if missing_ids:
            return Response(
                {"error": f"Students not found: {sorted(missing_ids)}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check for duplicates in this academic year
        existing_enrollments = set(
            Enrollment.objects.filter(
                student_id__in=student_ids,
                academic_year=academic_year
            ).values_list('student_id', flat=True)
        )
        if existing_enrollments:
            return Response(
                {"error": f"Students already enrolled this year: {sorted(existing_enrollments)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollments = []
        students_to_update = []
        for student_id in student_ids:
            student = existing_students[student_id]
            roll_no = student.roll_number if student.roll_number else 0
            enrollments.append(Enrollment(
                student_id=student_id,
                classname=classname,
                section=section,
                academic_year=academic_year,
                roll_no=roll_no,
            ))
            student.class_name_static = classname
            student.section_static = section
            students_to_update.append(student)

        with transaction.atomic():
            Enrollment.objects.bulk_create(enrollments)
            Student.objects.bulk_update(students_to_update, ['class_name_static', 'section_static'])

        return Response(
            {
                "message": f"Enrolled {len(enrollments)} students successfully.",
                "academic_year": academic_year,
                "classname": classname,
                "section": section,
                "count": len(enrollments),
            },
            status=status.HTTP_201_CREATED
        )
