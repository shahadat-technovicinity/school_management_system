from apps.attendance.models import Attendance
from rest_framework import serializers
from apps.students.models import Student
from django.contrib.auth import get_user_model

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
    classname = serializers.CharField(max_length=256)
    section = serializers.CharField(max_length=256)
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
    classname = serializers.CharField(max_length=256)
    section = serializers.CharField(max_length=256)
    date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=Attendance.STATUS_CHOICES
    )


class AttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'id',
            'date',
            'classname',
            'section',
            'status',
            'marked_by'
        ]