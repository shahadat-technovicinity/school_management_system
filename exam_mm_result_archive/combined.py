from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.students.models import Student
from .models import (
    CombinedResultConfig,
    StudentExamResult,
    calculate_grade_and_gpa,
)
from .views import overall_grade_from_cgpa


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
    দুটো বা বেশি বাছলে প্রতি subject এ মার্ক যোগ হয়, মোট পূর্ণমান দিয়ে percentage, তারপর Grade ও GPA।
    Subject এর combined grade F হলে সেই subject fail, কোনো subject fail হলে overall fail।
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
        students = students.select_related('section_static').order_by('section_static__name', 'roll_number')

        results = StudentExamResult.objects.filter(
            student__in=students,
            result_config__exam_routine__exam_setup__in=setups,
        ).select_related(
            'result_config__exam_routine__subject',
            'result_config__exam_routine__exam_name',
        )

        # student -> subject -> list of exam results
        grouped = {}
        for res in results:
            routine = res.result_config.exam_routine
            by_subject = grouped.setdefault(res.student_id, OrderedDict())
            by_subject.setdefault(routine.subject_id, {'name': routine.subject.name, 'items': []})
            by_subject[routine.subject_id]['items'].append((routine, res))

        student_list = []
        for student in students:
            by_subject = grouped.get(student.id, {})
            exam_map = OrderedDict()
            subject_rows = []
            grand_total = 0.0
            grand_full = 0.0
            total_gpa = 0.0
            all_passed = True

            for subject in by_subject.values():
                exams = []
                total = 0.0
                full = 0.0
                for routine, res in sorted(subject['items'], key=lambda x: x[0].exam_date):
                    total += float(res.total_marks)
                    full += float(routine.total_marks)

                    ex = exam_map.setdefault(routine.exam_setup_id, {
                        'setup_id': routine.exam_setup_id,
                        'exam': routine.exam_name.name,
                        'setup': setup_titles.get(routine.exam_setup_id, ''),
                        'subjects': [], 'gpa_sum': 0.0, 'passed': True,
                        'total': 0.0, 'full': 0.0,
                    })
                    ex['subjects'].append({
                        'subject': subject['name'],
                        'written_marks': res.written_marks,
                        'mcq_marks': res.mcq_marks,
                        'practical_marks': res.practical_marks,
                        'total_marks': res.total_marks,
                        'full_marks': routine.total_marks,
                        'grade': res.grade,
                        'gpa': float(res.gpa),
                        'status': res.overall_status,
                    })
                    ex['gpa_sum'] += float(res.gpa)
                    ex['total'] += float(res.total_marks)
                    ex['full'] += float(routine.total_marks)
                    if res.overall_status == 'fail' or res.grade == 'F':
                        ex['passed'] = False
                    exams.append({
                        'exam': routine.exam_name.name,
                        'marks': float(res.total_marks),
                        'full_marks': float(routine.total_marks),
                        'grade': res.grade,
                    })

                percentage = (total / full) * 100 if full > 0 else 0
                grade, gpa = calculate_grade_and_gpa(percentage)
                if grade == 'F':
                    all_passed = False

                grand_total += total
                grand_full += full
                total_gpa += gpa
                subject_rows.append({
                    'subject': subject['name'],
                    'exams': exams,
                    'total_marks': round(total, 2),
                    'full_marks': round(full, 2),
                    'percentage': round(percentage, 2),
                    'grade': grade,
                    'gpa': gpa,
                    'status': 'fail' if grade == 'F' else 'pass',
                })

            count = len(subject_rows)
            cgpa = round(total_gpa / count, 2) if count else 0.0
            if count == 0:
                overall_grade, cgpa = '-', 0.0
            elif not all_passed:
                overall_grade, cgpa = 'F', 0.0
            else:
                overall_grade = overall_grade_from_cgpa(cgpa)

            exam_wise = []
            for ex in exam_map.values():
                n = len(ex['subjects'])
                ex_cgpa = round(ex['gpa_sum'] / n, 2) if n else 0.0
                if not ex['passed']:
                    ex_grade, ex_cgpa = 'F', 0.0
                else:
                    ex_grade = overall_grade_from_cgpa(ex_cgpa)
                exam_wise.append({
                    'setup_id': ex['setup_id'],
                    'exam': ex['exam'],
                    'setup': ex['setup'],
                    'subject_wise_results': ex['subjects'],
                    'summary': {
                        'total_subjects': n,
                        'grand_total_marks': round(ex['total'], 2),
                        'grand_full_marks': round(ex['full'], 2),
                        'cgpa': ex_cgpa,
                        'overall_grade': ex_grade,
                        'overall_status': 'pass' if ex['passed'] else 'fail',
                    },
                })

            student_list.append({
                'student_id': student.id,
                'student_name': getattr(student, 'full_name', str(student)),
                'roll_number': student.roll_number,
                'section': student.section_static.name if student.section_static else '',
                'exam_wise_results': exam_wise,
                'combined': {
                  'subject_wise_results': subject_rows,
                  'summary': {
                    'total_subjects': count,
                    'grand_total_marks': round(grand_total, 2),
                    'grand_full_marks': round(grand_full, 2),
                    'cgpa': cgpa,
                    'overall_grade': overall_grade,
                    'overall_status': 'pass' if (all_passed and count > 0) else 'fail',
                  },
                },
            })

        return Response({
            'config_id': config.id,
            'name': config.name,
            'class': config.academic_class.name,
            'exams_combined': [str(s) for s in setups],
            'is_combined': len(setups) > 1,
            'total_students': len(student_list),
            'students': student_list,
        }, status=status.HTTP_200_OK)