
from apps.attendance.models import Attendance
from rest_framework import serializers
from apps.academics.models import ClassSection
from student_profile.models import StudentPersonalInfo
from teacher_mm_teacher.models import Teacher


class AttendanceRecordSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=StudentPersonalInfo.objects.all()
    )
    status = serializers.ChoiceField(
        choices=Attendance.STATUS_CHOICES
    )


class BulkAttendanceSerializer(serializers.Serializer):
    class_section = serializers.PrimaryKeyRelatedField(
        queryset=ClassSection.objects.all()
    )
    date = serializers.DateField()
    records = AttendanceRecordSerializer(many=True)
    marked_by = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all()
    )

    def create(self, validated_data):
        """
        UPSERT logic: create or update attendance
        """
        teacher = validated_data['marked_by']
        class_section = validated_data['class_section']
        date = validated_data['date']
        records = validated_data['records']

        attendances = []

        for record in records:
            obj, _ = Attendance.objects.update_or_create(
                student=record['student'],
                class_section=class_section,
                date=date,
                defaults={
                    'status': record['status'],
                    'marked_by': teacher
                }
            )
            attendances.append(obj)

        return attendances
