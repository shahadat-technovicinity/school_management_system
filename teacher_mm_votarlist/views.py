from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from apps.students.models import Student
from .serializers import ParentVoterListSerializer

# শুধু ডিজিটগুলোকে বাংলা সংখ্যায় করার জন্য
NUM_TO_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

class ParentVoterListView(APIView):
    pagination_class = None

    @swagger_auto_schema(
        responses={200: ParentVoterListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        students = Student.objects.select_related(
            'guardian_info', 
            'section_static'
        ).filter(
            status__in=['active', 'enrolled', 'Active']
        ).order_by(
            'class_name_static', 
            'section_static__name', 
            'roll_number'
        )

        voter_list = []
        guardian_voter_map = {}
        current_serial = 1

        EXCLUDE_FROM_GROUPING = ["N/A", "STRING", "TBA", "NONE", "", "এন/এ", "এন / এ"]

        for student in students:
            guardian = getattr(student, 'guardian_info', None)
            
            # Guardian Details Extractor
            father_name_bn = getattr(guardian, 'father_name_bn', '') if guardian else ''
            father_name = getattr(guardian, 'father_name', '') if guardian else ''
            mother_name_bn = getattr(guardian, 'mother_name_bn', '') if guardian else ''
            mother_name = getattr(guardian, 'mother_name', '') if guardian else ''

            # ১. অভিভাবকের নাম নির্ধারণ (বাংলা থাকলে আগে, না থাকলে ইংলিশ, তাও না থাকলে "এন/এ")
            voter_name = (
                father_name_bn.strip() or 
                father_name.strip() or 
                mother_name_bn.strip() or 
                mother_name.strip() or 
                "এন/এ"
            )

            # যদি ডাটাবেজে অভিভাবকের নাম "string" ডামি টেক্সট থাকে তবে এন/এ করে দেওয়া
            if voter_name.lower() in ["string", "tba"]:
                voter_name = "এন/এ"

            clean_voter_name = voter_name.strip().upper()

            # ২. সিবলিং লজিক ও ভোটার সিকুয়েন্স জেনারেটর (ফিক্সড)
            if clean_voter_name not in EXCLUDE_FROM_GROUPING and clean_voter_name in guardian_voter_map:
                voter_serial_str = guardian_voter_map[clean_voter_name]
            else:
                voter_serial_str = f"{current_serial:04d}".translate(NUM_TO_BN)
                if clean_voter_name not in EXCLUDE_FROM_GROUPING:
                    guardian_voter_map[clean_voter_name] = voter_serial_str
                current_serial += 1  # প্রতিটি ইউনিক প্রবেশের জন্য সিরিয়াল ১ করে বাড়বে

            # ৩. স্টুডেন্টের নাম (full_name_bn থাকলে নিবে, না থাকলে full_name)
            student_name = getattr(student, 'full_name_bn', '').strip() or getattr(student, 'full_name', '').strip()

            # ৪. কাস্টম প্রোপার্টি থেকে সরাসরি বাংলা ক্লাস ও সেকশনের নাম নেওয়া
            student_class_bn = getattr(student, 'class_label', '') or student.class_name_static or "এন/এ"
            section_name_bn = getattr(student, 'section_label', '') or (student.section_static.name if student.section_static else "এন/এ")

            # ৫. শুধু আইডি ও রোল সংখ্যাকে বাংলায় কনভার্ট করা
            class_roll_bn = str(student.roll_number).translate(NUM_TO_BN) if student.roll_number else "০"
            student_id_bn = str(student.id).translate(NUM_TO_BN)

            voter_list.append({
                "voter_number": voter_serial_str,
                "voter_name": voter_name,
                "student_name": student_name,
                "student_class": student_class_bn,
                "class_roll": class_roll_bn,
                "section_name": section_name_bn,
                "student_id": student_id_bn,
            })

        serializer = ParentVoterListSerializer(voter_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)