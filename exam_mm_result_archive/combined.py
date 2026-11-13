from collections import OrderedDict, defaultdict

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.students.models import Student
from .models import CombinedResultConfig, StudentExamResult
from .views import ScaleBook, load_group_map, summarize_student


class CombinedResultConfigSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='academic_class.name', read_only=True)
    setup_titles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CombinedResultConfig
        fields = [
            'id', 'name', 'academic_class', 'class_name',
            'exam_setups', 'setup_titles', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_setup_titles(self, obj):
        return [str(s) for s in obj.exam_setups.all()]

    def validate(self, attrs):
        academic_class = attrs.get('academic_class') or getattr(self.instance, 'academic_class', None)
        setups = attrs.get('exam_setups')
        if setups is None and self.instance:
            setups = list(self.instance.exam_setups.all())
        setups = setups or []

        if len(setups) < 1:
            raise serializers.ValidationError("কমপক্ষে একটা exam setup বাছতে হবে।")
        for setup in setups:
            if setup.academic_class_id != academic_class.id:
                raise serializers.ValidationError(
                    f"'{setup}' এই class এর setup না।"
                )
        return attrs


class CombinedResultConfigListCreateView(generics.ListCreateAPIView):
    queryset = CombinedResultConfig.objects.select_related('academic_class').prefetch_related('exam_setups')
    serializer_class = CombinedResultConfigSerializer


class CombinedResultConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CombinedResultConfig.objects.select_related('academic_class').prefetch_related('exam_setups')
    serializer_class = CombinedResultConfigSerializer


class CombinedResultView(APIView):
    """
    প্রতিটা exam এর নিজের result (exam_wise_results) এবং সবগুলো যোগ করা result (combined) দুটোই দেয়।
    একটা setup বাছলে combined মানে ওই একটা exam ই (is_combined = false)।
    দুটো বা বেশি বাছলে প্রতি বিষয়ে মার্ক যোগ হয়, মোট পূর্ণমান দিয়ে grade ও GPA হিসাব হয়।
    সব নিয়ম (English/Bangla দুই পেপার, ধর্ম বিষয়, ৪র্থ বিষয়) আলাদা আলাদা exam এ আর যোগফলে দুই জায়গাতেই চলে।
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, config_id):
        try:
            config = CombinedResultConfig.objects.select_related('academic_class').get(id=config_id)
        except CombinedResultConfig.DoesNotExist:
            return Response({'error': 'Combined result config পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        setups = list(config.exam_setups.prefetch_related('sections'))
        section_ids = {s.id for setup in setups for s in setup.sections.all()}
        setup_titles = {setup.id: str(setup) for setup in setups}

        section_id = request.query_params.get('section_id')
        student_id = request.query_params.get('student_id')

        students = Student.objects.filter(
            class_name_static_id=config.academic_class_id,
            section_static_id__in=section_ids,
        )
        if section_id:
            students = students.filter(section_static_id=section_id)
        if student_id:
            students = students.filter(id=student_id)
        students = list(students.select_related('section_static').order_by('section_static__name', 'roll_number'))

        results = StudentExamResult.objects.filter(
            student__in=students,
            result_config__exam_routine__exam_setup__in=setups,
        ).select_related(
            'result_config__exam_routine__subject',
            'result_config__exam_routine__exam_name',
            'result_config__exam_routine__academic_class',
        )

        by_student = defaultdict(list)
        for res in results:
            by_student[res.student_id].append(res)

        academic_class = config.academic_class
        scale_book, group_map = ScaleBook(academic_class.id), load_group_map()

        student_list = []
        for student in students:
            student_results = by_student.get(student.id, [])

            per_setup = OrderedDict()
            for res in student_results:
                per_setup.setdefault(res.result_config.exam_routine.exam_setup_id, []).append(res)

            exam_wise = []
            for setup_id, setup_results in per_setup.items():
                exam_data = summarize_student(student, setup_results, academic_class, scale_book, group_map)
                exam_wise.append({
                    'setup_id': setup_id,
                    'exam': setup_results[0].result_config.exam_routine.exam_name.name,
                    'setup': setup_titles.get(setup_id, ''),
                    **exam_data,
                })

            combined = summarize_student(
                student, student_results, academic_class, scale_book, group_map, check_components=False
            )

            student_list.append({
                'student_id': student.id,
                'student_name': getattr(student, 'full_name', str(student)),
                'roll_number': student.roll_number,
                'section': student.section_static.name if student.section_static else '',
                'exam_wise_results': exam_wise,
                'combined': combined,
            })

        return Response({
            'config_id': config.id,
            'name': config.name,
            'class': academic_class.name,
            'exams_combined': [str(s) for s in setups],
            'is_combined': len(setups) > 1,
            'total_students': len(student_list),
            'students': student_list,
        }, status=status.HTTP_200_OK)