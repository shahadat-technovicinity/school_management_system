from rest_framework import serializers
from .models import ExamRoutine
from exam_mm_exam_setup.models import ExamSetup


class ExamRoutineSerializer(serializers.ModelSerializer):
    exam_name_title = serializers.ReadOnlyField(source='exam_name.name')
    class_name_text = serializers.ReadOnlyField(source='academic_class.name')
    subject_name_text = serializers.ReadOnlyField(source='subject.name')
    
    # ExamSetup থেকে অটোমেটিক ক্লাস-ওয়াইজ সেকশন, শিফট ও টাইমিং রিড করা
    assigned_sections = serializers.SerializerMethodField()
    exam_shift = serializers.ReadOnlyField(source='exam_setup.shift', default=None)
    exam_time = serializers.ReadOnlyField(source='exam_setup.exam_time', default=None)

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
            'exam_time',
            'exam_date',
            'total_marks',
            'created_at'
        ]
        read_only_fields = ['exam_setup']

    def get_assigned_sections(self, obj):
        if obj.exam_setup:
            return [section.name for section in obj.exam_setup.sections.all()]
        
        # যদি কোনো কারণে save না থাকে, ক্যোয়ারি করে খুঁজে বের করা
        setup = ExamSetup.objects.filter(
            exam_name=obj.exam_name, 
            academic_class=obj.academic_class
        ).first()
        if setup:
            return [section.name for section in setup.sections.all()]
        return []

    def validate(self, attrs):
        # রুটিন তৈরি করার সময় ঐ exam_name এবং academic_class এর জন্য ExamSetup অস্তিত্ব আছে কিনা যাচাই
        exam_name = attrs.get('exam_name')
        academic_class = attrs.get('academic_class')

        setup_exists = ExamSetup.objects.filter(
            exam_name=exam_name,
            academic_class=academic_class
        ).exists()

        if not setup_exists:
            raise serializers.ValidationError(
                f"Selected Class '{academic_class.name}' has no Exam Setup for '{exam_name.name}'. Please create an Exam Setup first."
            )
        return attrs