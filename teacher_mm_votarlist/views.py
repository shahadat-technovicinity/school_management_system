from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from apps.students.models import Student
from .serializers import ParentVoterListSerializer

class ParentVoterListView(APIView):
    """
    Generates Parent Voter List for Active Students only, sorted by Class, Section, and Roll.
    Handles unique 4-digit serial numbering (0001, 0002) and sibling grouping.
    """
    @swagger_auto_schema(
        responses={200: ParentVoterListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        # ১. 'guardian_details' এর বদলে সঠিক Related Name 'guardian_info' ব্যবহার করা হলো
        students = Student.objects.select_related(
            'guardian_info', 
            'section_static'
        ).filter(
            status='active'
        ).order_by(
            'class_name_static', 
            'section_static__name', 
            'roll_number'
        )

        voter_list = []
        guardian_voter_map = {}
        current_serial = 1

        for student in students:
            # ২. guardian_details এর পরিবর্তে guardian_info নেওয়া হলো
            guardian = getattr(student, 'guardian_info', None)
            father_name = getattr(guardian, 'father_name', '') if guardian else ""
            mother_name = getattr(guardian, 'mother_name', '') if guardian else ""
            
            # Father name prioritize, fallback to mother name
            voter_name = father_name if (father_name and father_name != "TBA") else mother_name
            if not voter_name:
                voter_name = "N/A"

            # ৩. Sibling Check & 4-Digit Voter Serial Assignment (0001, 0002...)
            if voter_name in guardian_voter_map:
                voter_serial_str = guardian_voter_map[voter_name]
            else:
                voter_serial_str = f"{current_serial:04d}"
                if voter_name != "N/A":
                    guardian_voter_map[voter_name] = voter_serial_str
                current_serial += 1

            section_name = student.section_static.name if student.section_static else "N/A"

            voter_list.append({
                "voter_number": voter_serial_str,
                "voter_name": voter_name,
                "student_name": f"{student.first_name} {student.last_name}".strip(),
                "student_class": student.class_name_static,
                "class_roll": student.roll_number,
                "section_name": section_name,
                "student_id": student.admission_number,
            })

        serializer = ParentVoterListSerializer(voter_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)