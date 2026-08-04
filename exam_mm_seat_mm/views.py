from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from itertools import zip_longest

from .models import ExamRoom, ExamSession, RoomClassAssignment, SeatAssignment
from .serializers import (
    ExamRoomSerializer, ExamSessionSerializer,
    RoomClassAssignmentSerializer, SeatAssignmentSerializer
)
from apps.students.models import Student


# ---------------- ExamRoom ----------------
class ExamRoomListCreateView(generics.ListCreateAPIView):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer
    permission_classes = [IsAuthenticated]


class ExamRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer
    permission_classes = [IsAuthenticated]


# ---------------- ExamSession ----------------
class ExamSessionListCreateView(generics.ListCreateAPIView):
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [IsAuthenticated]


class ExamSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [IsAuthenticated]


# ---------------- RoomClassAssignment ----------------
class RoomClassAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = RoomClassAssignment.objects.all()
    serializer_class = RoomClassAssignmentSerializer
    permission_classes = [IsAuthenticated]


class RoomClassAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomClassAssignment.objects.all()
    serializer_class = RoomClassAssignmentSerializer
    permission_classes = [IsAuthenticated]


# ---------------- SeatAssignment ----------------
class SeatAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer
    permission_classes = [IsAuthenticated]


class SeatAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer
    permission_classes = [IsAuthenticated]


class SeatsByRoomView(generics.ListAPIView):
    """GET /api/exam-seat/seats/by-room/?exam_session=1&room=1"""
    serializer_class = SeatAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        exam_session_id = self.request.query_params.get('exam_session')
        room_id = self.request.query_params.get('room')
        return SeatAssignment.objects.filter(
            exam_session_id=exam_session_id, room_id=room_id
        ).order_by('bench_number')


class GenerateSeatPlanView(APIView):
    """
    POST /api/exam-seat/seats/generate/
    Body: { "exam_session": 1, "room": 1 }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam_session_id = request.data.get('exam_session')
        room_id = request.data.get('room')

        if not exam_session_id or not room_id:
            return Response(
                {"error": "exam_session এবং room দুটোই দিতে হবে।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room = ExamRoom.objects.get(id=room_id)
        except ExamRoom.DoesNotExist:
            return Response({"error": "Room পাওয়া যায়নি।"}, status=status.HTTP_404_NOT_FOUND)

        class_assignments = RoomClassAssignment.objects.filter(
            exam_session_id=exam_session_id, room_id=room_id
        )

        if not class_assignments.exists():
            return Response(
                {"error": "এই room-এ কোনো class assign করা নেই।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        class_student_lists = []
        for ca in class_assignments:
            students = list(
                Student.objects.filter(
                    class_name_static=ca.class_name,
                    section_static=ca.section,
                    status='active'
                ).order_by('id')
            )
            if students:
                class_student_lists.append({
                    'class_name': ca.class_name,
                    'section': ca.section,
                    'students': students
                })

        if not class_student_lists:
            return Response(
                {"error": "এই class/section গুলোতে কোনো active student পাওয়া যায়নি।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_students = sum(len(c['students']) for c in class_student_lists)
        if total_students > room.capacity:
            return Response(
                {"error": f"Room capacity ({room.capacity}) থেকে student সংখ্যা ({total_students}) বেশি।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        SeatAssignment.objects.filter(exam_session_id=exam_session_id, room_id=room_id).delete()

        student_queues = [c['students'] for c in class_student_lists]
        mixed_order = []
        for group in zip_longest(*student_queues, fillvalue=None):
            for student in group:
                if student is not None:
                    mixed_order.append(student)

        created_seats = []
        bench_number = 1
        per_bench = room.students_per_bench

        for i in range(0, len(mixed_order), per_bench):
            bench_students = mixed_order[i:i + per_bench]
            for student in bench_students:
                class_code = (student.class_name_static or '').replace('Class ', '')
                section_code = (student.section_static or '').replace('Section ', '')
                seat_label = f"{class_code}{section_code}-{bench_number:02d}"

                seat = SeatAssignment.objects.create(
                    exam_session_id=exam_session_id,
                    room=room,
                    student=student,
                    bench_number=bench_number,
                    seat_label=seat_label
                )
                created_seats.append(seat)
            bench_number += 1

        serializer = SeatAssignmentSerializer(created_seats, many=True)
        return Response(
            {"message": f"{len(created_seats)} জন student-কে সিট দেওয়া হয়েছে।", "seats": serializer.data},
            status=status.HTTP_201_CREATED
        )