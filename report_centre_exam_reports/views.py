from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count, Q
from apps.exams.models.setup import ExamSetup
from apps.exams.models.results import StudentResult
from .serializers import ExamReportSerializer


class ExamReportView(generics.GenericAPIView):
    serializer_class = ExamReportSerializer

    def get(self, request, *args, **kwargs):
        exam_setup_id = request.query_params.get('exam_setup')
        class_name_id = request.query_params.get('class_name')
        student_id = request.query_params.get('student')

        if not exam_setup_id:
            return Response({'error': 'exam_setup is required'}, status=400)

        results = StudentResult.objects.filter(
            exam_setup_id=exam_setup_id
        ).select_related('student', 'exam_setup', 'exam_setup__subject')

        if class_name_id:
            results = results.filter(exam_setup__class_name_id=class_name_id)

        if student_id:
            results = results.filter(student_id=student_id)

        total = results.count()
        passed = results.filter(
            marks_obtained__gte=results.first().exam_setup.pass_marks
        ).count() if results.exists() else 0
        failed = total - passed

        # Summary
        summary = results.aggregate(
            avg_marks=Avg('marks_obtained'),
            highest=Max('marks_obtained'),
            lowest=Min('marks_obtained'),
        )

        # Student list
        students = []
        for r in results:
            students.append({
                'student_id': r.student.admission_number,
                'name': r.student.full_name,
                'marks_obtained': r.marks_obtained,
                'total_marks': r.exam_setup.total_marks,
                'pass_marks': r.exam_setup.pass_marks,
                'grade': r.grade,
                'remarks': r.remarks,
                'status': 'Pass' if r.marks_obtained >= r.exam_setup.pass_marks else 'Fail',
            })

        return Response({
            'summary': {
                'total_students': total,
                'passed': passed,
                'failed': failed,
                'pass_percentage': round((passed / total) * 100, 1) if total else 0,
                'fail_percentage': round((failed / total) * 100, 1) if total else 0,
                'average_marks': round(summary['avg_marks'], 1) if summary['avg_marks'] else 0,
                'highest_marks': summary['highest'],
                'lowest_marks': summary['lowest'],
            },
            'students': students,
        })


class ClassPerformanceReportView(generics.GenericAPIView):
    serializer_class = ExamReportSerializer

    def get(self, request, *args, **kwargs):
        exam_setup_id = request.query_params.get('exam_setup')

        if not exam_setup_id:
            return Response({'error': 'exam_setup is required'}, status=400)

        # Class wise performance
        results = StudentResult.objects.filter(
            exam_setup_id=exam_setup_id
        ).select_related('exam_setup__class_name')

        class_data = {}
        for r in results:
            class_key = str(r.exam_setup.class_name)
            if class_key not in class_data:
                class_data[class_key] = {
                    'total': 0, 'passed': 0, 'marks_list': []
                }
            class_data[class_key]['total'] += 1
            class_data[class_key]['marks_list'].append(float(r.marks_obtained))
            if r.marks_obtained >= r.exam_setup.pass_marks:
                class_data[class_key]['passed'] += 1

        class_performance = []
        for class_name, data in class_data.items():
            total = data['total']
            passed = data['passed']
            marks_list = data['marks_list']
            class_performance.append({
                'class': class_name,
                'total_students': total,
                'passed': passed,
                'failed': total - passed,
                'pass_rate': round((passed / total) * 100, 1) if total else 0,
                'average_marks': round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
            })

        return Response({'class_performance': class_performance})


class SubjectPerformanceReportView(generics.GenericAPIView):
    serializer_class = ExamReportSerializer

    def get(self, request, *args, **kwargs):
        exam_setup_id = request.query_params.get('exam_setup')

        if not exam_setup_id:
            return Response({'error': 'exam_setup is required'}, status=400)

        results = StudentResult.objects.filter(
            exam_setup_id=exam_setup_id
        ).select_related('exam_setup__subject')

        subject_data = {}
        for r in results:
            subject_key = str(r.exam_setup.subject)
            if subject_key not in subject_data:
                subject_data[subject_key] = {
                    'total': 0, 'passed': 0, 'marks_list': []
                }
            subject_data[subject_key]['total'] += 1
            subject_data[subject_key]['marks_list'].append(float(r.marks_obtained))
            if r.marks_obtained >= r.exam_setup.pass_marks:
                subject_data[subject_key]['passed'] += 1

        subject_performance = []
        for subject, data in subject_data.items():
            total = data['total']
            passed = data['passed']
            marks_list = data['marks_list']
            subject_performance.append({
                'subject': subject,
                'total_students': total,
                'passed': passed,
                'failed': total - passed,
                'pass_rate': round((passed / total) * 100, 1) if total else 0,
                'average_marks': round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
                'highest': max(marks_list) if marks_list else 0,
                'lowest': min(marks_list) if marks_list else 0,
            })

        return Response({'subject_performance': subject_performance})


class IndividualStudentReportView(generics.GenericAPIView):
    serializer_class = ExamReportSerializer

    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student')
        exam_setup_id = request.query_params.get('exam_setup')

        if not student_id:
            return Response({'error': 'student is required'}, status=400)

        results = StudentResult.objects.filter(
            student_id=student_id
        ).select_related('exam_setup', 'exam_setup__subject', 'student')

        if exam_setup_id:
            results = results.filter(exam_setup_id=exam_setup_id)

        subjects = []
        total_marks = 0
        obtained_marks = 0

        for r in results:
            subjects.append({
                'subject': str(r.exam_setup.subject),
                'total_marks': r.exam_setup.total_marks,
                'marks_obtained': r.marks_obtained,
                'pass_marks': r.exam_setup.pass_marks,
                'grade': r.grade,
                'status': 'Pass' if r.marks_obtained >= r.exam_setup.pass_marks else 'Fail',
                'remarks': r.remarks,
            })
            total_marks += float(r.exam_setup.total_marks)
            obtained_marks += float(r.marks_obtained)

        student = results.first().student if results.exists() else None

        return Response({
            'student': {
                'id': student.admission_number if student else '',
                'name': student.full_name if student else '',
            },
            'subjects': subjects,
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'percentage': round((obtained_marks / total_marks) * 100, 1) if total_marks else 0,
        })