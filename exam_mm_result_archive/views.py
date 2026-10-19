from rest_framework import generics, filters, pagination, parsers, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from .models import ExamResultConfig, StudentExamResult
from .serializers import (
    ExamResultConfigSerializer,
    StudentExamResultSerializer,
    StudentListForResultSerializer,
    BulkResultInputSerializer,
)


class ResultPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ExamResultConfigListCreateView(generics.ListCreateAPIView):
    queryset = ExamResultConfig.objects.all().select_related('exam_routine')
    serializer_class = ExamResultConfigSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class ExamResultConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamResultConfig.objects.all().select_related('exam_routine')
    serializer_class = ExamResultConfigSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class StudentListByClassSectionView(generics.GenericAPIView):
    serializer_class = StudentListForResultSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('result_config_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        result_config_id = request.query_params.get('result_config_id')

        if not class_id:
            return Response({'error': 'class_id is required'}, status=400)

        try:
            academic_class = AcademicClass.objects.get(id=class_id)
        except AcademicClass.DoesNotExist:
            return Response({'error': 'Class not found'}, status=404)

        # পরিবর্তন: নামের পরিবর্তে সরাসরি অবজেক্ট বা ID পাস করা হলো
        students = Student.objects.filter(class_name_static=academic_class) 
        # অথবা যদি আইডি ফিল্ড হয়: class_name_static_id=academic_class.id

        if section_id:
            try:
                section = Section.objects.get(id=section_id)
                students = students.filter(section_static=section)
                # অথবা যদি আইডি ফিল্ড হয়: section_static_id=section.id
            except Section.DoesNotExist:
                return Response({'error': 'Section not found'}, status=404)

        students = students.order_by('roll_number')

        config_data = None
        if result_config_id:
            try:
                config = ExamResultConfig.objects.get(id=result_config_id)
                config_data = ExamResultConfigSerializer(config).data
            except ExamResultConfig.DoesNotExist:
                pass

        student_list = []
        for student in students:
            existing_result = None
            if result_config_id:
                result = StudentExamResult.objects.filter(
                    student=student,
                    result_config_id=result_config_id
                ).first()
                if result:
                    existing_result = StudentExamResultSerializer(result).data

            student_list.append({
                'id': student.id,
                'full_name': student.full_name,
                'roll_number': student.roll_number,
                'admission_number': student.admission_number,
                'existing_result': existing_result,
            })

        return Response({
            'class': academic_class.name,
            'has_practical': academic_class.id in [4, 5],
            'result_config': config_data,
            'students': student_list,
        })


class StudentExamResultListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentExamResultSerializer
    pagination_class = ResultPagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__first_name', 'student__last_name', 'overall_status']

    def get_queryset(self):
        queryset = StudentExamResult.objects.all().select_related('student', 'result_config', 'section')
        config_id = self.request.query_params.get('result_config')
        section_id = self.request.query_params.get('section')
        overall_status = self.request.query_params.get('overall_status')

        if config_id:
            queryset = queryset.filter(result_config_id=config_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        if overall_status:
            queryset = queryset.filter(overall_status=overall_status)

        return queryset


class StudentExamResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentExamResult.objects.all().select_related('student', 'result_config')
    serializer_class = StudentExamResultSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class BulkResultInputView(generics.GenericAPIView):
    serializer_class = BulkResultInputSerializer
    parser_classes = [parsers.JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        result_config_id = data['result_config']
        section_id = data.get('section')
        results = data['results']

        try:
            config = ExamResultConfig.objects.get(id=result_config_id)
        except ExamResultConfig.DoesNotExist:
            return Response({'error': 'Result config not found'}, status=404)

        section = None
        if section_id:
            try:
                section = Section.objects.get(id=section_id)
            except Section.DoesNotExist:
                pass

        created = []
        updated = []
        errors = []

        for item in results:
            student_id = item.get('student')
            written_marks = item.get('written_marks', 0)
            mcq_marks = item.get('mcq_marks', 0)
            practical_marks = item.get('practical_marks', 0) if config.has_practical else 0

            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                errors.append({'student': student_id, 'error': 'Student not found'})
                continue

            result, is_created = StudentExamResult.objects.update_or_create(
                result_config=config,
                student=student,
                defaults={
                    'written_marks': written_marks,
                    'mcq_marks': mcq_marks,
                    'practical_marks': practical_marks,
                    'section': section,
                }
            )

            if is_created:
                created.append(student_id)
            else:
                updated.append(student_id)

        return Response({
            'message': f'{len(created)} created, {len(updated)} updated',
            'created': created,
            'updated': updated,
            'errors': errors,
        }, status=status.HTTP_200_OK)