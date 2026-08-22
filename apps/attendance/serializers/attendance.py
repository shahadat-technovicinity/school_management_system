from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.attendance.models import Attendance
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section

User = get_user_model()


class AttendanceRecordSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all()
    )
    status = serializers.ChoiceField(
        choices=Attendance.STATUS_CHOICES
    )


class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    classname = serializers.PrimaryKeyRelatedField(
        queryset=AcademicClass.objects.all()
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all()
    )
    records = AttendanceRecordSerializer(many=True)
    marked_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__name='Teacher')
    )

    def create(self, validated_data):
        user = validated_data['marked_by']
        classname = validated_data['classname']
        section = validated_data['section']
        date = validated_data['date']
        records = validated_data['records']

        attendances = []

        for record in records:
            obj, _ = Attendance.objects.update_or_create(
                student=record['student'],
                classname=classname,
                section=section,
                date=date,
                defaults={
                    'status': record['status'],
                    'marked_by': user
                }
            )
            attendances.append(obj)

        return attendances


class AttendancePatchSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all()
    )
    classname = serializers.PrimaryKeyRelatedField(
        queryset=AcademicClass.objects.all()
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all()
    )
    date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=Attendance.STATUS_CHOICES
    )


class AttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'date',
            'classname',
            'section',
            'status',
            'marked_by'
        ]