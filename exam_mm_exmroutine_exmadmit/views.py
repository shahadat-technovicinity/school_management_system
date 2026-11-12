from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ExamsRoutine
from .utils import student_takes_subject, subject_religion
from exam_mm_exam_setup.models import ExamSetup
from apps.students.models import Student
from .serializers import (
    ExamRoutineSerializer,
    ExamRoutineBulkCreateSerializer,
    SingleStudentAdmitCardSerializer,
    ExamRoutineItemForAdmitCardSerializer
)


class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamsRoutine.objects.select_related(
        'exam_name',
        'academic_class',
        'subject',
        'exam_setup'
    ).prefetch_related(
        'exam_setup__sections'
    ).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamRoutineBulkCreateSerializer
        return ExamRoutineSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        setup_id = self.request.query_params.get('exam_setup')
        if setup_id:
            queryset = queryset.filter(exam_setup_id=setup_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_routines = serializer.save()

        response_serializer = ExamRoutineSerializer(created_routines, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamsRoutine.objects.all()
    serializer_class = ExamRoutineSerializer


class ClassWiseAdmitCardGenerateView(generics.GenericAPIView):
    serializer_class = SingleStudentAdmitCardSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Generate Admit Cards",
        operation_description="class_id (Required) এবং exam_setup_id অথবা (exam_id + section_id) দিতে হবে। student_id optional।",
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, description="Academic Class ID (Required)",
                              type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, description="Specific Exam Setup ID",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('exam_id', openapi.IN_QUERY, description="Exam Name ID (section_id সহ দিতে হবে)",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section_id', openapi.IN_QUERY, description="Section ID",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('student_id', openapi.IN_QUERY, description="Optional: specific Student ID",
                              type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('class_id')
        setup_id = request.query_params.get('exam_setup_id')
        exam_id = request.query_params.get('exam_id')
        section_id = request.query_params.get('section_id')
        student_id = request.query_params.get('student_id')

        if not class_id:
            return Response(
                {"error": "'class_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Exam Setup (section-specific)
        if setup_id:
            exam_setup = get_object_or_404(ExamSetup, id=setup_id, academic_class_id=class_id)
        elif exam_id and section_id:
            exam_setup = get_object_or_404(
                ExamSetup,
                exam_name_id=exam_id,
                academic_class_id=class_id,
                sections__id=section_id
            )
        else:
            return Response(
                {"error": "'exam_setup_id' অথবা ('exam_id' + 'section_id') দিতে হবে।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exam_name = exam_setup.exam_name
        academic_class = exam_setup.academic_class

        # 2. শুধু এই setup এর routine
        routines = ExamsRoutine.objects.filter(
            exam_setup=exam_setup
        ).select_related('subject').order_by('exam_date', 'start_time')

        routine_list = list(routines)
        routine_data = ExamRoutineItemForAdmitCardSerializer(routine_list, many=True).data
        routine_pairs = list(zip(routine_list, routine_data))
        has_religion_subject = any(subject_religion(r.subject) for r in routine_list)

        # কোন বিষয় ধর্ম/ঐচ্ছিক হিসেবে ধরা হলো, সেটা দেখানো হয় যাতে ভুল ধরলে বোঝা যায়
        detected_subjects = [
            {
                "subject": r.subject.name,
                "religion": subject_religion(r.subject) or None,
                "is_optional": d["is_optional"],
            }
            for r, d in routine_pairs
            if subject_religion(r.subject) or d["is_optional"]
        ]

        # 3. Students
        students_queryset = Student.objects.filter(class_name_static=academic_class)

        if section_id:
            if not exam_setup.sections.filter(id=section_id).exists():
                return Response(
                    {"error": "এই section এই exam setup এ নেই।"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            students_queryset = students_queryset.filter(section_static_id=section_id)
        else:
            students_queryset = students_queryset.filter(section_static__in=exam_setup.sections.all())

        if student_id:
            students_queryset = students_queryset.filter(id=student_id)

        students = students_queryset.select_related(
            'class_name_static', 'section_static'
        ).order_by('section_static__name', 'roll_number')

        # 4. Response (প্রতিটা ছাত্রের নিজের ধর্ম বিষয় অনুযায়ী routine)
        admit_cards = []
        warnings = []
        for student in students:
            student_info = SingleStudentAdmitCardSerializer(student).data
            student_info['shift'] = exam_setup.shift

            student_routines = [
                data for routine, data in routine_pairs
                if student_takes_subject(student, routine.subject)
            ]

            if has_religion_subject and not any(
                subject_religion(r.subject) and student_takes_subject(student, r.subject)
                for r, _ in routine_pairs
            ):
                warnings.append(
                    f"{student.full_name} (roll {student.roll_number or '-'}): "
                    f"ধর্ম বিষয় পাওয়া যায়নি (প্রোফাইলে ধর্ম: {student.religion or 'দেওয়া নেই'})"
                )

            admit_cards.append({
                "exam_title": exam_name.name,
                "student_info": student_info,
                "routines": student_routines
            })

        return Response({
            "exam_setup_id": exam_setup.id,
            "exam_id": exam_name.id,
            "exam_title": exam_name.name,
            "class_id": academic_class.id,
            "class_name": academic_class.name,
            "total_students": len(admit_cards),
            "detected_subjects": detected_subjects,
            "warnings": warnings,
            "admit_cards": admit_cards
        }, status=status.HTTP_200_OK)