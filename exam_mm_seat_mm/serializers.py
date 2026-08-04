from rest_framework import serializers
from .models import ExamRoom, ExamSession, RoomClassAssignment, SeatAssignment
from apps.students.models import Student


class ExamRoomSerializer(serializers.ModelSerializer):
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = ExamRoom
        fields = [
            'id', 'room_number', 'number_of_benches',
            'students_per_bench', 'is_available', 'capacity'
        ]


class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = ['id', 'name', 'date', 'shift']


class RoomClassAssignmentSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = RoomClassAssignment
        fields = [
            'id', 'exam_session', 'room', 'room_number',
            'class_name', 'section', 'subject'
        ]


class StudentMiniSerializer(serializers.ModelSerializer):
    """Seat plan-এ student এর basic info দেখানোর জন্য"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'roll_number', 'class_name_static', 'section_static', 'photo']


class SeatAssignmentSerializer(serializers.ModelSerializer):
    student_detail = StudentMiniSerializer(source='student', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = SeatAssignment
        fields = [
            'id', 'exam_session', 'room', 'room_number',
            'student', 'student_detail', 'bench_number', 'seat_label'
        ]