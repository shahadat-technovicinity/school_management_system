from rest_framework import status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.utils.dateparse import parse_date
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.pagination.standard_pagination import StandardPagination
from apps.common.views.basemodelview import BaseModelViewSet
from apps.enrollments.models import Enrollment
from apps.enrollments.serializers.enrollments import EnrollmentSerializer, BulkEnrollmentSerializer
from apps.students.models import Student
from apps.academics.models import AcademicYear


class EnrollmentViewSet(BaseModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'classname', 'section').all()
    serializer_class = EnrollmentSerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'classname', 'section', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'classname__name', 'section__name']
    ordering_fields = ['created_at', 'updated_at']

    authentication_classes = [JWTAuthentication]

    def _sync_student_info(self, enrollment):
        student = enrollment.student
        if student:
            update_fields = []

            if enrollment.classname:
                student.class_name_static = enrollment.classname.name
                update_fields.append('class_name_static')

            if enrollment.section:
                student.section_static = enrollment.section.name
                update_fields.append('section_static')

            if enrollment.academic_year:
                student.academic_year = str(enrollment.academic_year)
                update_fields.append('academic_year')

            if update_fields:
                student.save(update_fields=update_fields)

    def perform_create(self, serializer):
        enrollment = serializer.save()
        self._sync_student_info(enrollment)

    def perform_update(self, serializer):
        enrollment = serializer.save()
        self._sync_student_info(enrollment)

    def perform_destroy(self, instance):
        student = instance.student
        instance.delete()
        if student:
            latest_enrollment = Enrollment.objects.filter(student=student).order_by('-id').first()
            if latest_enrollment:
                self._sync_student_info(latest_enrollment)
            else:
                student.class_name_static = None
                student.section_static = None
                student.save(update_fields=['class_name_static', 'section_static'])

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()

        queryset = super().get_queryset()

        date_param = self.request.query_params.get('date') or self.request.query_params.get('attendance_date')
        academic_year_param = self.request.query_params.get('academic_year')

        target_year = None

        if academic_year_param:
            target_year = str(academic_year_param)
        elif date_param:
            parsed_dt = parse_date(str(date_param))
            if parsed_dt:
                target_year = str(parsed_dt.year)
            else:
                clean_date = str(date_param).replace('/', '-')
                parts = clean_date.split('-')
                target_year = next((part for part in parts if len(part) == 4 and part.isdigit()), None)

        if not target_year:
            target_year = str(timezone.now().year)

        queryset = queryset.filter(academic_year=str(target_year))

        return queryset.distinct()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student', openapi.IN_QUERY, description="Student ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('classname', openapi.IN_QUERY, description="Class ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('academic_year', openapi.IN_QUERY, description="Academic Year ID/Name", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Date for attendance filtering", type=openapi.TYPE_STRING),
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

        self._sync_student_info(enrollment)

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

            # Class name update
            class_obj = None
            section_obj = None
            try:
                from apps.academics.models import AcademicClass, Section
                class_obj = AcademicClass.objects.get(id=class_id)
                section_obj = Section.objects.get(id=section_id)
            except Exception:
                pass

            if class_obj:
                student.class_name_static = class_obj.name
            if section_obj:
                student.section_static = section_obj.name
            if hasattr(student, 'academic_year'):
                student.academic_year = year_str

            students_to_update.append(student)

        with transaction.atomic():
            Enrollment.objects.bulk_create(enrollments)

            update_fields = ['class_name_static', 'section_static', 'academic_year']
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