import openpyxl
from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import IntegerField, Value
from django.db.models.functions import Cast, Coalesce, NullIf

from apps.students.models import Student
from .serializers import ParentVoterListSerializer

# ইংরেজি থেকে বাংলা ডিজিট রূপান্তর
NUM_TO_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def get_processed_voter_list():
    """
    ভোটার লিস্ট প্রসেস করার কমন লজিক (API এবং Excel Export উভয়ের জন্য)
    স্ট্যাটাস ফিল্টার বাদ দেওয়া হয়েছে যাতে সকল স্টুডেন্ট চলে আসে।
    """
    queryset = Student.objects.select_related(
        'guardian_info', 
        'section_static',
        'class_name_static'
    ).annotate(
        safe_roll_str=NullIf('roll_number', Value('')),
        roll_int=Cast(Coalesce('safe_roll_str', Value('0')), IntegerField())
    ).order_by(
        'class_name_static', 
        'section_static__name', 
        'roll_int'
    )

    students = list(queryset)

    # টার্মিনালে চেক করার জন্য প্রিন্ট
    print(f"--- DEBUG: Total Students Fetched from DB: {len(students)} ---")

    voter_list = []
    guardian_voter_map = {}
    current_serial = 1

    EXCLUDE_FROM_GROUPING = ["N/A", "STRING", "TBA", "NONE", "", "এন/এ", "এন / এ"]

    for student in students:
        guardian = getattr(student, 'guardian_info', None)
        
        # Guardian Details
        father_name_bn = getattr(guardian, 'father_name_bn', '') if guardian else ''
        father_name = getattr(guardian, 'father_name', '') if guardian else ''
        mother_name_bn = getattr(guardian, 'mother_name_bn', '') if guardian else ''
        mother_name = getattr(guardian, 'mother_name', '') if guardian else ''

        voter_name = (
            father_name_bn.strip() or 
            father_name.strip() or 
            mother_name_bn.strip() or 
            mother_name.strip() or 
            "এন/এ"
        )

        if voter_name.lower() in ["string", "tba"]:
            voter_name = "এন/এ"

        clean_voter_name = voter_name.strip().upper()

        # সিবলিং ও ভোটার সিকুয়েন্স
        if clean_voter_name not in EXCLUDE_FROM_GROUPING and clean_voter_name in guardian_voter_map:
            voter_serial_str = guardian_voter_map[clean_voter_name]
        else:
            voter_serial_str = f"{current_serial:04d}".translate(NUM_TO_BN)
            if clean_voter_name not in EXCLUDE_FROM_GROUPING:
                guardian_voter_map[clean_voter_name] = voter_serial_str
            current_serial += 1

        student_name = getattr(student, 'full_name_bn', '').strip() or getattr(student, 'full_name', '').strip()

        # AcademicClass অবজেক্টকে নিরাপদে স্ট্রিং এ কনভার্ট করা
        if getattr(student, 'class_label', ''):
            student_class_bn = student.class_label
        elif student.class_name_static:
            student_class_bn = getattr(student.class_name_static, 'name', str(student.class_name_static))
        else:
            student_class_bn = "এন/এ"

        section_name_bn = getattr(student, 'section_label', '') or (student.section_static.name if student.section_static else "এন/এ")

        # রোল নম্বর ফরম্যাট
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
        responses={200: ParentVoterListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        voter_list = get_processed_voter_list()
        serializer = ParentVoterListSerializer(voter_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportParentVoterListExcelView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Excel File Download",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        voter_list = get_processed_voter_list()

        # Excel Workbook ও Sheet তৈরি
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "অভিভাবক ভোটার তালিকা"

        # এক্সেল হেডার
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

        # ডাটা রো অ্যাপেন্ড করা
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

        # মেমোরিতে ফাইলটি সেভ করে রেসপন্স আকারে পাঠানো
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Parent_Voter_List.xlsx"'
        return response