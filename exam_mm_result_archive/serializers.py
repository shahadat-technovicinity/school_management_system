from rest_framework import serializers
from apps.students.models import Student
from .models import ExamMark, SubjectPassMarkConfig, GradeScale


def convert_eng_to_bng_digits(text):
    if text is None:
        return ""
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


class SubjectPassMarkConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPassMarkConfig
        fields = '__all__'
        read_only_fields = ['total_full_mark']


class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'


class StudentInfoFilterSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'roll_number', 'class_name_static', 'section_static']


class SingleMarkInputSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    writing = serializers.FloatField(default=0, required=False)
    mcq = serializers.FloatField(default=0, required=False)
    practical = serializers.FloatField(default=0, required=False)


class MarkSubmissionSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100)
    exam_type = serializers.CharField(max_length=100)
    marks_data = SingleMarkInputSerializer(many=True)

    def create(self, validated_data):
        subject = validated_data['subject']
        exam_type = validated_data['exam_type']
        marks_list = validated_data['marks_data']

        created_or_updated = []
        for mark_item in marks_list:
            student_obj = Student.objects.get(id=mark_item['student_id'])
            exam_mark, _ = ExamMark.objects.update_or_create(
                student=student_obj,
                subject=subject,
                exam_type=exam_type,
                defaults={
                    'writing': mark_item.get('writing', 0),
                    'mcq': mark_item.get('mcq', 0),
                    'practical': mark_item.get('practical', 0),
                    'status': 'pending'
                }
            )
            created_or_updated.append(exam_mark)

        return {"message": f"Successfully saved {len(created_or_updated)} student marks."}


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)

    class Meta:
        model = ExamMark
        fields = [
            'id', 'student', 'student_name', 'roll_number', 'subject', 'exam_type',
            'writing', 'mcq', 'practical', 'total', 'grade_point',
            'letter_grade', 'is_passed', 'status', 'updated_at'
        ]
        read_only_fields = ['total', 'grade_point', 'letter_grade', 'is_passed']


class MarkStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamMark
        fields = ['id', 'status']


class FinalResultSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id', read_only=True)
    total_marks = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    result_status = serializers.SerializerMethodField()
    failed_subject_count = serializers.SerializerMethodField()
    merit_position = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'full_name', 'roll_number', 
            'total_marks', 'gpa', 'result_status', 
            'failed_subject_count', 'merit_position'
        ]

    def _is_swagger(self):
        request = self.context.get('request')
        if not request:
            return True
        return getattr(request.parser_context.get('view', None), 'swagger_fake_view', False)

    def get_total_marks(self, obj):
        if self._is_swagger():
            return 0.0
        exam_type = self.context.get('exam_type')
        marks = ExamMark.objects.filter(student=obj, status='approved')
        if exam_type:
            marks = marks.filter(exam_type=exam_type)
        return sum(m.total for m in marks)

    def get_failed_subject_count(self, obj):
        if self._is_swagger():
            return 0
        exam_type = self.context.get('exam_type')
        marks = ExamMark.objects.filter(student=obj, status='approved')
        if exam_type:
            marks = marks.filter(exam_type=exam_type)
        return marks.filter(is_passed=False).count()

    def get_gpa(self, obj):
        if self._is_swagger():
            return 0.0
        
        if self.get_failed_subject_count(obj) > 0:
            return 0.0

        exam_type = self.context.get('exam_type')
        marks = ExamMark.objects.filter(student=obj, status='approved')
        if exam_type:
            marks = marks.filter(exam_type=exam_type)

        if not marks.exists():
            return 0.0

        total_gp = sum(m.grade_point for m in marks)
        return round(total_gp / marks.count(), 2)

    def get_result_status(self, obj):
        if self._is_swagger():
            return "PASSED"
        failed_count = self.get_failed_subject_count(obj)
        if failed_count > 0:
            return f"FAILED ({failed_count} Subject{'s' if failed_count > 1 else ''})"
        return "PASSED"

    def get_merit_position(self, obj):
        if self._is_swagger():
            return 1
        if self.get_failed_subject_count(obj) > 0:
            return None
            
        merit_map = self.context.get('merit_map', {})
        return merit_map.get(obj.id, None)