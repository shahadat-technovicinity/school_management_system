from rest_framework import generics, filters, pagination, parsers, status
from rest_framework.views import APIView
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




class StudentDetailedMarksheetView(APIView):
    """
    একই API দিয়ে class_id ও section_id মাধ্যমে পুরো ক্লাসের অথবা 
    student_id দিয়ে নির্দিষ্ট একজন স্টুডেন্টের সাবজেক্ট-ওয়াইজ রেজাল্ট ও CGPA দেখা যাবে।
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Class ID"),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Section ID (Optional)"),
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Student ID (Single Student Search)"),
            openapi.Parameter('result_config_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Result Config ID (Optional)"),
        ]
    )
    def get(self, request, student_id=None):
        # URL kwarg (যেমন /student-marksheet/15/) অথবা Query Param (?student_id=15) দুটিই হ্যান্ডেল করবে
        search_student_id = student_id or request.query_params.get('student_id')
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        result_config_id = request.query_params.get('result_config_id')

        # স্টুডেন্টের ফলাফল প্রোসেস করার হেলপার ফাংশন
        def process_student_result(student):
            results_qs = StudentExamResult.objects.filter(student=student).select_related(
                'result_config', 'result_config__exam_routine', 'section'
            )
            if result_config_id:
                results_qs = results_qs.filter(result_config_id=result_config_id)

            subject_results = []
            grand_total_marks = 0
            total_gpa = 0.0
            is_overall_passed = True
            subject_count = results_qs.count()

            for res in results_qs:
                config = res.result_config
                subject_name = getattr(config.exam_routine, 'subject_name', str(config.exam_routine))

                subject_results.append({
                    "subject_id": config.id,
                    "subject": subject_name,
                    "written_marks": res.written_marks,
                    "mcq_marks": res.mcq_marks,
                    "practical_marks": res.practical_marks if config.has_practical else 0,
                    "total_marks": res.total_marks,
                    "grade": res.grade,
                    "gpa": float(res.gpa),
                    "status": res.overall_status
                })

                grand_total_marks += float(res.total_marks)
                total_gpa += float(res.gpa)

                if res.overall_status == 'fail' or res.grade == 'F':
                    is_overall_passed = False

            cgpa = round(total_gpa / subject_count, 2) if subject_count > 0 else 0.0
            
            if not is_overall_passed or subject_count == 0:
                overall_grade = 'F' if subject_count > 0 else '-'
            else:
                if cgpa >= 5.0: overall_grade = 'A+'
                elif cgpa >= 4.0: overall_grade = 'A'
                elif cgpa >= 3.5: overall_grade = 'A-'
                elif cgpa >= 3.0: overall_grade = 'B'
                elif cgpa >= 2.0: overall_grade = 'C'
                elif cgpa >= 1.0: overall_grade = 'D'
                else: overall_grade = 'F'

            return {
                "student_id": student.id,
                "student_name": getattr(student, 'full_name', getattr(student, 'name', str(student))),
                "roll_number": getattr(student, 'roll_number', ''),
                "section": getattr(student.section_static, 'name', '') if hasattr(student, 'section_static') and student.section_static else '',
                "subject_wise_results": subject_results,
                "summary": {
                    "total_subjects": subject_count,
                    "grand_total_marks": grand_total_marks,
                    "cgpa": cgpa,
                    "overall_grade": overall_grade,
                    "overall_status": "pass" if (is_overall_passed and subject_count > 0) else "fail"
                }
            }

        # ১. যদি স্টুডেন্ট আইডি দেওয়া থাকে (URL বা Query Parameter)
        if search_student_id:
            try:
                student = Student.objects.get(id=search_student_id)
            except Student.DoesNotExist:
                return Response({'error': 'নির্দিষ্ট স্টুডেন্টটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(process_student_result(student), status=status.HTTP_200_OK)

        # ২. যদি ক্লাস আইডি দেওয়া থাকে (Class & Section Search)
        if class_id:
            try:
                academic_class = AcademicClass.objects.get(id=class_id)
            except AcademicClass.DoesNotExist:
                return Response({'error': 'ক্লাসটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

            students = Student.objects.filter(class_name_static=academic_class, status="active")
            
            section_obj = None
            if section_id:
                try:
                    section_obj = Section.objects.get(id=section_id)
                    students = students.filter(section_static=section_obj)
                except Section.DoesNotExist:
                    return Response({'error': 'সেকশনটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

            students = students.order_by('roll_number')
            student_list = [process_student_result(s) for s in students]

            return Response({
                "class": academic_class.name,
                "section": section_obj.name if section_obj else "All Sections",
                "total_students": len(student_list),
                "students": student_list
            }, status=status.HTTP_200_OK)

        return Response({'error': 'অনুগ্রহ করে `class_id` অথবা `student_id` প্রদান করুন।'}, status=status.HTTP_400_BAD_REQUEST)