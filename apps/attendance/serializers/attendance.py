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

    def validate(self, attrs):
        classname = attrs.get('classname')
        section = attrs.get('section')
        date = attrs.get('date')

        # ওই তারিখ, ক্লাস এবং সেকশনে ইতোপূর্বে এটেনডেন্স জমা হয়েছে কিনা তা চেক করা
        existing_attendance = Attendance.objects.filter(
            classname=classname,
            section=section,
            date=date
        ).exists()

        if existing_attendance:
            raise serializers.ValidationError({
                "detail": f"Attendance for class '{classname}' and section '{section}' on {date} has already been submitted."
            })

        return attrs

    def create(self, validated_data):
        user = validated_data['marked_by']
        classname = validated_data['classname']
        section = validated_data['section']
        date = validated_data['date']
        records = validated_data['records']

        attendances = [
            Attendance(
                student=record['student'],
                classname=classname,
                section=section,
                date=date,
                status=record['status'],
                marked_by=user
            )
            for record in records
        ]

        # একবারে ডাটাবেজে এন্ট্রি করার জন্য bulk_create ব্যবহার করা হয়েছে
        return Attendance.objects.bulk_create(attendances)


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