from rest_framework import serializers
from .models import ExamsRoutine
from .utils import subject_is_optional
from academic_create_subject.models import Subject_Name
from exam_mm_exam_setup.models import ExamSetup
from apps.students.models import Student


class ExamRoutineSerializer(serializers.ModelSerializer):
    exam_name_title = serializers.ReadOnlyField(source='exam_name.name')
    class_name_text = serializers.ReadOnlyField(source='academic_class.name')
    subject_name_text = serializers.ReadOnlyField(source='subject.name')

    assigned_sections = serializers.SerializerMethodField()
    exam_shift = serializers.ReadOnlyField(source='exam_setup.shift', default=None)

    class Meta:
        model = ExamsRoutine
        fields = [
            'id',
            'exam_name',
            'exam_name_title',
            'academic_class',
            'class_name_text',
            'subject',
            'subject_name_text',
            'exam_setup',
            'assigned_sections',
            'exam_shift',
            'exam_date',
            'start_time',
            'end_time',
            'total_marks',
            'created_at',
        ]
        read_only_fields = ['exam_name', 'academic_class']

    def get_assigned_sections(self, obj):
        if obj.exam_setup:
            return [section.name for section in obj.exam_setup.sections.all()]
        return []


class RoutineSubjectItemSerializer(serializers.Serializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject_Name.objects.all())
    exam_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    total_marks = serializers.DecimalField(max_digits=5, decimal_places=2)


class ExamRoutineBulkCreateSerializer(serializers.Serializer):
    exam_setup = serializers.PrimaryKeyRelatedField(queryset=ExamSetup.objects.all())
    routines = RoutineSubjectItemSerializer(many=True)

    def create(self, validated_data):
        exam_setup = validated_data['exam_setup']
        routine_objects = [
            ExamsRoutine(
                exam_setup=exam_setup,
                exam_name=exam_setup.exam_name,
                academic_class=exam_setup.academic_class,
                subject=item['subject'],
                exam_date=item['exam_date'],
                start_time=item['start_time'],
                end_time=item['end_time'],
                total_marks=item['total_marks'],
            )
            for item in validated_data['routines']
        ]
        return ExamsRoutine.objects.bulk_create(routine_objects)


class SingleStudentAdmitCardSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id')
    student_name = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='class_name_static.name', default='')
    section_name = serializers.CharField(source='section_static.name', default='')
    roll_no = serializers.CharField(source='roll_number', default='N/A')

    class Meta:
        model = Student
        fields = ['student_id', 'student_name', 'class_name', 'section_name', 'roll_no']

    def get_student_name(self, obj):
        name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return name if name else "N/A"


class ExamRoutineItemForAdmitCardSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.name')
    is_optional = serializers.SerializerMethodField()

    class Meta:
        model = ExamsRoutine
        fields = ['subject_name', 'is_optional', 'exam_date', 'start_time', 'end_time', 'total_marks']

    def get_is_optional(self, obj):
        return subject_is_optional(obj.subject)