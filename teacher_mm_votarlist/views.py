from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from apps.students.models import Student
from .serializers import ParentVoterListSerializer

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

        # সিবলিং ফিল্টার থেকে বাদ দেওয়ার জন্য ডামি নামের লিস্ট
        EXCLUDE_FROM_GROUPING = ["N/A", "STRING", "TBA", "NONE", ""]

        for student in students:
            guardian = getattr(student, 'guardian_info', None)
            father_name = getattr(guardian, 'father_name', '') if guardian else ""
            mother_name = getattr(guardian, 'mother_name', '') if guardian else ""
            
            voter_name = father_name if (father_name and father_name != "TBA") else mother_name
            if not voter_name:
                voter_name = "N/A"

            clean_voter_name = voter_name.strip().upper()

            # সিবলিং চেক: নাম আসল হলে এবং পূর্বে ম্যাপে থাকলে আগের সিরিয়াল পাবে
            if clean_voter_name not in EXCLUDE_FROM_GROUPING and clean_voter_name in guardian_voter_map:
                voter_serial_str = guardian_voter_map[clean_voter_name]
            else:
                voter_serial_str = f"{current_serial:04d}"
                if clean_voter_name not in EXCLUDE_FROM_GROUPING:
                    guardian_voter_map[clean_voter_name] = voter_serial_str
                current_serial += 1

            section_name = student.section_static.name if student.section_static else "N/A"

            voter_list.append({
                "voter_number": voter_serial_str,
                "voter_name": voter_name,
                "student_name": f"{student.first_name} {student.last_name}".strip(),
                "student_class": student.class_name_static,
                "class_roll": student.roll_number,
                "section_name": section_name,
                "student_id": str(student.id),  # স্ক্রিনশট অনুযায়ী আসল স্টুডেন্ট ID
            })

        serializer = ParentVoterListSerializer(voter_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)