from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.pagination.standard_pagination import StandardPagination
from apps.common.views.basemodelview import BaseModelViewSet
from apps.enrollments.models import Enrollment
from apps.enrollments.serializers.enrollments import EnrollmentSerializer, BulkEnrollmentSerializer
from apps.students.models import Student
from apps.academics.models import AcademicYear


class EnrollmentViewSet(BaseModelViewSet):
    """
    CRUD API for Enrollment.
    Supports filtering, search and ordering via query params.
    """
    # 🟢 academic_year Non-relational field হওয়ায় select_related থেকে সরিয়ে দেওয়া হয়েছে
    queryset = Enrollment.objects.select_related('student', 'classname', 'section').all()
    serializer_class = EnrollmentSerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'classname', 'section', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'classname__name', 'section__name']
    ordering_fields = ['created_at', 'updated_at']

    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student', openapi.IN_QUERY, description="Student ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('classname', openapi.IN_QUERY, description="Class ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('academic_year', openapi.IN_QUERY, description="Academic Year ID/Name", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search across student name", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student = serializer.validated_data['student']
        academic_year = serializer.validated_data['academic_year']
        classname = serializer.validated_data['classname']
        section = serializer.validated_data['section']

        enrollment, created = Enrollment.objects.update_or_create(
            student=student,
            academic_year=academic_year,
            defaults={
                'classname': classname,
                'section': section,
                'roll_no': 0,
            }
        )

        # Student মডেল আপডেট
        if hasattr(student, 'class_name_static_id'):
            student.class_name_static_id = classname.id if hasattr(classname, 'id') else classname
        if hasattr(student, 'section_static_id'):
            student.section_static_id = section.id if hasattr(section, 'id') else section
        if hasattr(student, 'academic_year'):
            student.academic_year = str(academic_year)
            
        student.save()

        response_serializer = self.get_serializer(enrollment)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=status_code)

    @swagger_auto_schema(
        request_body=BulkEnrollmentSerializer,
        responses={
            201: openapi.Response("Bulk enrollment created successfully"),
            400: "Bad request - duplicate enrollment or missing active year",
            404: "Students not found",
        }
    )
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        serializer = BulkEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        students_data = data['students']
        class_id = data['classname']
        section_id = data['section']
        academic_year_id = data.get('academic_year')

        student_ids = [item['student_id'] for item in students_data]

        if not academic_year_id:
            active_year = AcademicYear.objects.filter(is_active=True).first()
            if not active_year:
                return Response(
                    {"error": "No active academic year found in the system."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            academic_year_id = active_year.id

        students_qs = Student.objects.filter(id__in=student_ids)
        existing_students = {s.id: s for s in students_qs}
        missing_ids = set(student_ids) - set(existing_students.keys())
        if missing_ids:
            return Response(
                {"error": f"Students not found: {sorted(missing_ids)}"},
                status=status.HTTP_404_NOT_FOUND
            )

        existing_enrollments = set(
            Enrollment.objects.filter(
                student_id__in=student_ids,
                academic_year=str(academic_year_id)
            ).values_list('student_id', flat=True)
        )
        if existing_enrollments:
            return Response(
                {"error": f"Students already enrolled in this academic year: {sorted(existing_enrollments)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollments = []
        students_to_update = []

        academic_year_obj = AcademicYear.objects.filter(id=academic_year_id).first()
        year_str = str(academic_year_obj) if academic_year_obj else str(academic_year_id)

        for item in students_data:
            s_id = item['student_id']
            student = existing_students[s_id]

            enrollments.append(Enrollment(
                student_id=s_id,
                classname_id=class_id,
                section_id=section_id,
                academic_year=year_str,
                roll_no=0,
            ))

            if hasattr(student, 'class_name_static_id'):
                student.class_name_static_id = class_id
            if hasattr(student, 'section_static_id'):
                student.section_static_id = section_id
            if hasattr(student, 'academic_year'):
                student.academic_year = year_str

            students_to_update.append(student)

        with transaction.atomic():
            Enrollment.objects.bulk_create(enrollments)
            
            update_fields = []
            if hasattr(Student, 'class_name_static'):
                update_fields.append('class_name_static')
            if hasattr(Student, 'section_static'):
                update_fields.append('section_static')
            if hasattr(Student, 'academic_year'):
                update_fields.append('academic_year')
                
            if update_fields:
                Student.objects.bulk_update(students_to_update, update_fields)

        return Response(
            {
                "message": f"Successfully enrolled {len(enrollments)} students.",
                "academic_year": year_str,
                "classname_id": class_id,
                "section_id": section_id,
                "count": len(enrollments),
            },
            status=status.HTTP_201_CREATED
        )