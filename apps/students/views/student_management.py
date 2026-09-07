from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from apps.students.models import Student
from apps.students.serializers.management_serializers import StudentManagementSerializer
from apps.enrollments.models import Enrollment


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class StudentManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Student Grid/List view and adding/updating students.
    """
    serializer_class = StudentManagementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['status', 'academic_year', 'gender', 'blood_group', 'class_name_static', 'section_static']
    search_fields = ['first_name', 'last_name', 'admission_number', 'roll_number', 'primary_contact_number']
    ordering_fields = ['created_at', 'admission_date', 'first_name']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()

        return Student.objects.select_related(
            'guardian_info',
            'additional_info'
        ).prefetch_related(
            'disciplinary_records',
            'enrollment_set', 
            'enrollment_set__classname', 
            'enrollment_set__section'
        ).all().order_by('-created_at').distinct()

    def _sync_enrollment(self, student):
        """
        Student এর ইনস্ট্যান্স থেকেই সরাসরি Academic Class, Section এবং Academic Year নিয়ে Enrollment তৈরি করবে।
        """
        # স্টুডেন্ট মডেল থেকে ক্লাস ও সেকশন ফরেইন কি (FK) অবজেক্ট নেওয়া হচ্ছে
        class_obj = getattr(student, 'class_name_static', None) or getattr(student, 'classname', None)
        section_obj = getattr(student, 'section_static', None) or getattr(student, 'section', None)

        # যদি মডেলের অবজেক্ট হিসেবে না পাওয়া যায়, তবে রিকোয়েস্ট ডাটা থেকে ট্রাই করবে
        if not class_obj:
            class_id = self.request.data.get('class_name_static') or self.request.data.get('classname') or self.request.data.get('class_id')
        else:
            class_id = class_obj.id if hasattr(class_obj, 'id') else class_obj

        if not section_obj:
            section_id = self.request.data.get('section_static') or self.request.data.get('section') or self.request.data.get('section_id')
        else:
            section_id = section_obj.id if hasattr(section_obj, 'id') else section_obj

        academic_year = student.academic_year or self.request.data.get('academic_year') or '2026'
        roll_no = getattr(student, 'roll_number', None) or self.request.data.get('roll_number') or 0

        # যদি ক্লাস এবং সেকশন আইডি পাওয়া যায় তবেই এনরোলমেন্ট তৈরি বা আপডেট হবে
        if class_id and section_id:
            Enrollment.objects.update_or_create(
                student=student,
                academic_year=str(academic_year),
                defaults={
                    'classname_id': class_id,
                    'section_id': section_id,
                    'roll_no': roll_no
                }
            )

    def perform_create(self, serializer):
        with transaction.atomic():
            student = serializer.save()
            self._sync_enrollment(student)

    def perform_update(self, serializer):
        with transaction.atomic():
            student = serializer.save()
            self._sync_enrollment(student)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)