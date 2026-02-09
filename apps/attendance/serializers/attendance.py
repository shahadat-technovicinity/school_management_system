from apps.attendance.models import Attendance
from rest_framework import serializers
from academic_class_routine.models import Teacher



class AttendanceRecordSerializer(serializers.Serializer):
    student = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=[Attendance.PRESENT, Attendance.ABSENT]
    )


class BulkAttendanceRequestSerializer(serializers.Serializer):
    class_section = serializers.IntegerField()
    date = serializers.DateField()
    marked_by = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all()
    )
    records = AttendanceRecordSerializer(many=True)

