from rest_framework import serializers
from apps.students.models import Student
from .models import ExamResultConfig, StudentExamResult


def check_student_matches_routine(student, routine):
    """Student এর class ও section routine এর setup এর সাথে মিলছে কিনা দেখে।
    মিললে None, না মিললে error message return করে।"""
    if student.class_name_static_id != routine.academic_class_id:
        return "Student এর class এই routine এর class এর সাথে মিলছে না।"

    setup = routine.exam_setup
    if setup is not None:
        section_id = student.section_static_id
        if not section_id or not setup.sections.filter(id=section_id).exists():
            return "Student এর section এই exam setup এ নেই।"
    return None


class ExamResultConfigSerializer(serializers.ModelSerializer):
    has_practical = serializers.BooleanField(read_only=True)
    subject_name = serializers.CharField(source='exam_routine.subject.name', read_only=True)
    class_name = serializers.CharField(source='exam_routine.academic_class.name', read_only=True)
    total_full_marks = serializers.DecimalField(
        source='exam_routine.total_marks',
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = ExamResultConfig
        fields = '__all__'
        extra_kwargs = {
            'written_full_marks': {'required': False},
            'written_pass_marks': {'required': False},
            'mcq_full_marks': {'required': False},
            'mcq_pass_marks': {'required': False},
            'practical_full_marks': {'required': False},
            'practical_pass_marks': {'required': False},
        }


class StudentExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    student_roll = serializers.SerializerMethodField(read_only=True)
    has_practical = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentExamResult
        fields = '__all__'
        read_only_fields = [
            'total_marks', 'grade', 'gpa',
            'written_status', 'mcq_status',
            'practical_status', 'overall_status',
        ]
        extra_kwargs = {
            'practical_marks': {'required': False},
            'section': {'required': False},
        }

    def get_student_name(self, obj):
        return obj.student.full_name

    def get_student_roll(self, obj):
        return obj.student.roll_number

    def get_has_practical(self, obj):
        return obj.result_config.has_practical

    def validate(self, data):
        result_config = data.get('result_config') or getattr(self.instance, 'result_config', None)
        student = data.get('student') or getattr(self.instance, 'student', None)

        if result_config and student:
            error = check_student_matches_routine(student, result_config.exam_routine)
            if error:
                raise serializers.ValidationError(error)

        if result_config and not result_config.has_practical:
            data['practical_marks'] = 0

        return data


class StudentListForResultSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'roll_number', 'admission_number']


class BulkResultInputSerializer(serializers.Serializer):
    result_config = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())

    def validate_results(self, value):
        for item in value:
            if 'student' not in item:
                raise serializers.ValidationError("প্রতিটি item এ student id লাগবে")
            if 'written_marks' not in item:
                raise serializers.ValidationError("written_marks লাগবে")
            if 'mcq_marks' not in item:
                raise serializers.ValidationError("mcq_marks লাগবে")
        return value