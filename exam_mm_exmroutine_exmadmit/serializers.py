from rest_framework import serializers
from .models import ExamRoutine
from academic_create_subject.models import Subject_Name
from academic_mm_class_and_section.models import AcademicClass
from exam_mm_exam_setup.models import ExamName, ExamSetup
from apps.students.models import Student


class ExamRoutineSerializer(serializers.ModelSerializer):
    exam_name_title = serializers.ReadOnlyField(source='exam_name.name')
    class_name_text = serializers.ReadOnlyField(source='academic_class.name')
    subject_name_text = serializers.ReadOnlyField(source='subject.name')
    
    assigned_sections = serializers.SerializerMethodField()
    exam_shift = serializers.ReadOnlyField(source='exam_setup.shift', default=None)

    class Meta:
        model = ExamRoutine
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
            'created_at'
        ]
        read_only_fields = ['exam_setup']

    def get_assigned_sections(self, obj):
        if obj.exam_setup:
            return [section.name for section in obj.exam_setup.sections.all()]
        
        setup = ExamSetup.objects.filter(
            exam_name=obj.exam_name, 
            academic_class=obj.academic_class
        ).first()
        if setup:
            return [section.name for section in setup.sections.all()]
        return []


class RoutineSubjectItemSerializer(serializers.Serializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject_Name.objects.all())
    exam_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    total_marks = serializers.DecimalField(max_digits=5, decimal_places=2)


class ExamRoutineBulkCreateSerializer(serializers.Serializer):
    exam_name = serializers.PrimaryKeyRelatedField(queryset=ExamName.objects.all())
    academic_class = serializers.PrimaryKeyRelatedField(queryset=AcademicClass.objects.all())
    routines = RoutineSubjectItemSerializer(many=True)

    def validate(self, attrs):
        exam_name = attrs.get('exam_name')
        academic_class = attrs.get('academic_class')

        setup = ExamSetup.objects.filter(
            exam_name=exam_name,
            academic_class=academic_class
        ).first()

        if not setup:
            raise serializers.ValidationError(
                f"Selected Class '{academic_class.name}' has no Exam Setup for '{exam_name.name}'. Please create an Exam Setup first."
            )
        attrs['exam_setup'] = setup
        return attrs

    def create(self, validated_data):
        exam_name = validated_data['exam_name']
        academic_class = validated_data['academic_class']
        exam_setup = validated_data['exam_setup']
        routines_data = validated_data['routines']

        routine_objects = [
            ExamRoutine(
                exam_name=exam_name,
                academic_class=academic_class,
                exam_setup=exam_setup,
                subject=item['subject'],
                exam_date=item['exam_date'],
                start_time=item['start_time'],
                end_time=item['end_time'],
                total_marks=item['total_marks']
            )
            for item in routines_data
        ]

        return ExamRoutine.objects.bulk_create(routine_objects)


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

    class Meta:
        model = ExamRoutine
        fields = ['subject_name', 'exam_date', 'start_time', 'end_time', 'total_marks']