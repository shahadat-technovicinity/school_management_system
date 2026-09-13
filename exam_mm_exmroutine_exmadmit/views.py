from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ExamRoutine
from exam_mm_exam_setup.models import ExamSetup
from apps.students.models import Student
from .serializers import (
    ExamRoutineSerializer, 
    ExamRoutineBulkCreateSerializer,
    SingleStudentAdmitCardSerializer,
    ExamRoutineItemForAdmitCardSerializer
)


class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamRoutine.objects.select_related(
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_routines = serializer.save()

        response_serializer = ExamRoutineSerializer(created_routines, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineSerializer


class ClassWiseAdmitCardGenerateView(generics.GenericAPIView):
    serializer_class = SingleStudentAdmitCardSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Generate Admit Cards",
        operation_description="Search and generate admit cards using class_id (Required). Exam ID, Section ID, and Student ID are optional.",
        manual_parameters=[
            openapi.Parameter(
                'class_id', 
                openapi.IN_QUERY, 
                description="ID of the Academic Class (Required)", 
                type=openapi.TYPE_INTEGER, 
                required=True
            ),
            openapi.Parameter(
                'exam_id', 
                openapi.IN_QUERY, 
                description="Optional: Specific Exam ID (If not provided, latest exam setup will be picked)", 
                type=openapi.TYPE_INTEGER, 
                required=False
            ),
            openapi.Parameter(
                'section_id', 
                openapi.IN_QUERY, 
                description="Optional: ID of specific Section", 
                type=openapi.TYPE_INTEGER, 
                required=False
            ),
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="Optional: ID of specific Student", 
                type=openapi.TYPE_INTEGER, 
                required=False
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('class_id')
        exam_id = request.query_params.get('exam_id')
        section_id = request.query_params.get('section_id')
        student_id = request.query_params.get('student_id')

        if not class_id:
            return Response(
                {"error": "'class_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Fetch Exam Setup
        if exam_id:
            exam_setup = get_object_or_404(ExamSetup, exam_name_id=exam_id, academic_class_id=class_id)
        else:
            exam_setup = ExamSetup.objects.filter(academic_class_id=class_id).last()
            if not exam_setup:
                return Response(
                    {"error": f"No Exam Setup found for class_id '{class_id}'."},
                    status=status.HTTP_404_NOT_FOUND
                )

        exam_name = exam_setup.exam_name
        academic_class = exam_setup.academic_class

        # 2. Fetch Exam Routines
        routines = ExamRoutine.objects.filter(
            exam_name=exam_name,
            academic_class=academic_class
        ).select_related('subject').order_by('exam_date', 'start_time')

        routine_data = ExamRoutineItemForAdmitCardSerializer(routines, many=True).data

        # 3. Filter Students using actual model fields (class_name_static, section_static)
        students_queryset = Student.objects.filter(class_name_static=academic_class)

        if section_id:
            students_queryset = students_queryset.filter(section_static_id=section_id)
        else:
            students_queryset = students_queryset.filter(section_static__in=exam_setup.sections.all())

        if student_id:
            students_queryset = students_queryset.filter(id=student_id)

        students = students_queryset.select_related('class_name_static', 'section_static').order_by('section_static__name', 'roll_number')

        # 4. Construct Output Response
        admit_cards = []
        for student in students:
            student_info = SingleStudentAdmitCardSerializer(student).data
            student_info['shift'] = exam_setup.shift

            admit_cards.append({
                "exam_title": exam_name.name,
                "student_info": student_info,
                "routines": routine_data
            })

        return Response({
            "exam_id": exam_name.id,
            "exam_title": exam_name.name,
            "class_id": academic_class.id,
            "class_name": academic_class.name,
            "total_students": len(admit_cards),
            "admit_cards": admit_cards
        }, status=status.HTTP_200_OK)