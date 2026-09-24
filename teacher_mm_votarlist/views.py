import openpyxl
from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q, IntegerField, Value
from django.db.models.functions import Cast, Coalesce, NullIf

from apps.students.models import Student
from .serializers import ParentVoterListSerializer

# English to Bangla digit translation
NUM_TO_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def get_processed_voter_list(academic_year=None):
    """
    Voter list process korar logic.
    Student model-er academic_year field shothikbhabe filter kora hochhe.
    """
    queryset = Student.objects.select_related(
        'guardian_info', 
        'section_static',
        'class_name_static'
    )

    # Academic Year filter logic
    if academic_year is not None and str(academic_year).strip() != "":
        clean_year = str(academic_year).strip()

        # If academic_year parameter is ID or numeric
        if clean_year.isdigit():
            queryset = queryset.filter(
                Q(academic_year_id=int(clean_year)) | Q(academic_year=clean_year)
            )
        # If academic_year is a String (e.g. "2026")
        else:
            queryset = queryset.filter(
                Q(academic_year__name__icontains=clean_year) | Q(academic_year=clean_year)
            )

    queryset = queryset.annotate(
        safe_roll_str=NullIf('roll_number', Value('')),
        roll_int=Cast(Coalesce('safe_roll_str', Value('0')), IntegerField())
    ).order_by(
        'class_name_static', 
        'section_static__name', 
        'roll_int'
    )

    students = list(queryset)

    # Terminal debug print
    print(f"--- DEBUG: Filter Parameter Received: '{academic_year}' ---")
    print(f"--- DEBUG: Total Students Fetched: {len(students)} ---")

    voter_list = []
    guardian_voter_map = {}
    current_serial = 1

    EXCLUDE_FROM_GROUPING = ["N/A", "STRING", "TBA", "NONE", "", "এন/এ", "এন / এ"]

    for student in students:
        guardian = getattr(student, 'guardian_info', None)
        
        # Guardian Details (Bangla name check)
        father_name_bn = getattr(guardian, 'father_name_bn', '') if guardian else ''
        mother_name_bn = getattr(guardian, 'mother_name_bn', '') if guardian else ''

        father_name_bn_clean = father_name_bn.strip() if father_name_bn else ''
        mother_name_bn_clean = mother_name_bn.strip() if mother_name_bn else ''

        voter_name = (
            father_name_bn_clean or 
            mother_name_bn_clean or 
            "এন/এ"
        )

        if voter_name.lower() in ["string", "tba"]:
            voter_name = "এন/এ"

        clean_voter_name = voter_name.strip().upper()

        # Sibling and voter sequence grouping
        if clean_voter_name not in EXCLUDE_FROM_GROUPING and clean_voter_name in guardian_voter_map:
            voter_serial_str = guardian_voter_map[clean_voter_name]
        else:
            voter_serial_str = f"{current_serial:04d}".translate(NUM_TO_BN)
            if clean_voter_name not in EXCLUDE_FROM_GROUPING:
                guardian_voter_map[clean_voter_name] = voter_serial_str
            current_serial += 1

        # Student Name
        raw_student_name_bn = getattr(student, 'full_name_bn', '')
        student_name = raw_student_name_bn.strip() if raw_student_name_bn else "এন/এ"

        # Class Label
        if getattr(student, 'class_label', ''):
            student_class_bn = student.class_label
        elif student.class_name_static:
            student_class_bn = getattr(student.class_name_static, 'name', str(student.class_name_static))
        else:
            student_class_bn = "এন/এ"

        # Section Label
        section_name_bn = getattr(student, 'section_label', '') or (student.section_static.name if student.section_static else "এন/এ")

        # Roll Number and ID formatting
        raw_roll = str(student.roll_number).strip() if student.roll_number else "0"
        class_roll_bn = raw_roll.translate(NUM_TO_BN) if raw_roll else "০"
        student_id_bn = str(student.id).translate(NUM_TO_BN)

        voter_list.append({
            "voter_number": voter_serial_str,
            "voter_name": voter_name,
            "student_name": student_name,
            "student_class": str(student_class_bn),
            "class_roll": class_roll_bn,
            "section_name": str(section_name_bn),
            "student_id": student_id_bn,
        })

    return voter_list


class ParentVoterListView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'academic_year',
                openapi.IN_QUERY,
                description="Academic Year ID or Name (e.g. 1 or 2026)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: ParentVoterListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        academic_year = request.query_params.get('academic_year')
        voter_list = get_processed_voter_list(academic_year=academic_year)
        serializer = ParentVoterListSerializer(voter_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportParentVoterListExcelView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'academic_year',
                openapi.IN_QUERY,
                description="Academic Year ID or Name (e.g. 1 or 2026)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Excel File Download",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        academic_year = request.query_params.get('academic_year')
        voter_list = get_processed_voter_list(academic_year=academic_year)

        # Excel Workbook creation
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "অভিভাবক ভোটার তালিকা"

        # Headers
        headers = [
            "ভোটার নম্বর", 
            "ভোটারের নাম", 
            "শিক্ষার্থীর নাম", 
            "শ্রেণী", 
            "রোল", 
            "শাখা", 
            "স্টুডেন্ট আইডি"
        ]
        ws.append(headers)

        # Append Data
        for item in voter_list:
            ws.append([
                item["voter_number"],
                item["voter_name"],
                item["student_name"],
                item["student_class"],
                item["class_roll"],
                item["section_name"],
                item["student_id"]
            ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Parent_Voter_List.xlsx"'
        return response