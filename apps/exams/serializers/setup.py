from rest_framework import serializers
from ..models.setup import ExamSetup, ExamType, Subject, ExamRoutine, QuestionBank, QuestionType

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

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'
        ref_name = 'AppsExamsQuestionBankSerializer'
