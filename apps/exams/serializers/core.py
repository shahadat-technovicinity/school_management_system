from rest_framework import serializers
from ..models import ExamSetup, ExamType, Subject, ExamRoutine, TeacherDuty, StudentResult

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ExamSetupSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.ReadOnlyField(source='exam_type.name')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    class_name_str = serializers.ReadOnlyField(source='class_name.name')

    class Meta:
        model = ExamSetup
        fields = '__all__'

class ExamRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRoutine
        fields = '__all__'

class TeacherDutySerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.user.get_full_name')
    
    class Meta:
        model = TeacherDuty
        fields = '__all__'

class StudentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.get_full_name')
    
    class Meta:
        model = StudentResult
        fields = '__all__'
