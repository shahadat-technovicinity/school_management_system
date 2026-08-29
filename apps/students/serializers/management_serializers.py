from rest_framework import serializers
from django.db import transaction
from apps.students.models import Student, GuardianDetails, AdditionalDetails, StudentDiscipline
from apps.enrollments.models import Enrollment


class GuardianDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianDetails
        exclude = ('student',)


class AdditionalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails
        exclude = ('student',)


class StudentDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDiscipline
        fields = '__all__'


class StudentManagementSerializer(serializers.ModelSerializer):
    guardian_info = GuardianDetailsSerializer(required=False)
    additional_info = AdditionalDetailsSerializer(required=False)
    disciplinary_records = StudentDisciplineSerializer(many=True, read_only=True)
    
    attendance_percentage = serializers.SerializerMethodField()
    disciplinary_status = serializers.SerializerMethodField()
    
    class_label = serializers.SerializerMethodField()
    section_label = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def get_class_label(self, obj):
        # Fresh DB Lookup: Get the latest enrollment object
        enrollment = Enrollment.objects.filter(student_id=obj.id).select_related('classname').order_by('-id').first()
        
        if enrollment and enrollment.classname:
            return getattr(enrollment.classname, 'name', str(enrollment.classname))
        
        # Fallback to static class name if no enrollment exists
        if hasattr(obj, 'class_name_static') and obj.class_name_static:
            return getattr(obj.class_name_static, 'name', str(obj.class_name_static))

        return ""

    def get_section_label(self, obj):
        # Fresh DB Lookup: Get the latest enrollment section
        enrollment = Enrollment.objects.filter(student_id=obj.id).select_related('section').order_by('-id').first()
        
        if enrollment and enrollment.section:
            return getattr(enrollment.section, 'name', str(enrollment.section))

        # Fallback to static section name if no enrollment exists
        if hasattr(obj, 'section_static') and obj.section_static:
            return getattr(obj.section_static, 'name', str(obj.section_static))

        return ""

    def get_attendance_percentage(self, obj):
        return 85.5 

    def get_disciplinary_status(self, obj):
        if obj.disciplinary_records.filter(severity='high').exists():
            return "At Risk"
        return "Good Standing"

    @transaction.atomic
    def create(self, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        student = Student.objects.create(**validated_data)

        if guardian_data:
            GuardianDetails.objects.create(student=student, **guardian_data)
        if additional_data:
            AdditionalDetails.objects.create(student=student, **additional_data)

        # Student তৈরি হওয়ার সাথে সাথে ইনিশিয়াল Enrollment তৈরি করা
        if student.class_name_static and student.section_static:
            try:
                Enrollment.objects.create(
                    student=student,
                    classname=student.class_name_static,
                    section=student.section_static,
                    academic_year=getattr(student, 'academic_year', '2026')
                )
            except Exception:
                pass

        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if guardian_data:
            GuardianDetails.objects.update_or_create(
                student=instance,
                defaults=guardian_data
            )
        if additional_data:
            AdditionalDetails.objects.update_or_create(
                student=instance,
                defaults=additional_data
            )

        return instance