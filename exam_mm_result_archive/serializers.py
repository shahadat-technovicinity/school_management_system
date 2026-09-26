from rest_framework import serializers
from apps.students.models import Student
from academic_create_subject.models import Subject_Name
from exam_mm_exam_setup.models import ExamName
from .models import ExamMark, SubjectPassMarkConfig, GradeScale


class SubjectPassMarkConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPassMarkConfig
        fields = '__all__'


class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'


class StudentInfoFilterSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'student_name', 'class_name_static', 'section_static']

    def get_student_name(self, obj):
        if getattr(obj, 'full_name', None):
            return obj.full_name
        if getattr(obj, 'name', None):
            return obj.name
        return f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip() or "N/A"


class StudentMarkInputSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    writing = serializers.FloatField(required=False, default=0)
    mcq = serializers.FloatField(required=False, default=0)
    practical = serializers.FloatField(required=False, default=0)


class MarkSubmissionSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    exam_type = serializers.PrimaryKeyRelatedField(queryset=ExamName.objects.all())
    marks_data = StudentMarkInputSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        subject_id = validated_data.pop('subject_id')
        exam_type = validated_data.pop('exam_type')
        marks_data_list = validated_data.pop('marks_data')

        try:
            subject_obj = Subject_Name.objects.get(id=subject_id)
        except Subject_Name.DoesNotExist:
            raise serializers.ValidationError({"error": f"Subject with ID {subject_id} not found."})

        score_objects = []
        for mark_data in marks_data_list:
            student_id = mark_data['student_id']
            try:
                student_obj = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"error": f"Student with ID {student_id} not found."})

            mark_obj, created = ExamMark.objects.update_or_create(
                student=student_obj,
                subject=subject_obj,
                exam_type=exam_type,
                defaults={
                    'writing': mark_data.get('writing', 0),
                    'mcq': mark_data.get('mcq', 0),
                    'practical': mark_data.get('practical', 0),
                    'status': 'pending'
                }
            )
            score_objects.append(mark_obj)

        return {'message': 'Marks successfully submitted for admin approval.', 'count': len(score_objects)}

    def to_representation(self, instance):
        return {
            "status": "success",
            "message": instance['message'],
            "records_processed": instance['count']
        }


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamMark
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'subject', 'subject_name', 'exam_type', 'writing', 'mcq', 'practical',
            'total', 'grade_point', 'letter_grade', 'is_passed', 'status'
        ]
        read_only_fields = ['total', 'grade_point', 'letter_grade', 'is_passed', 'status']


class MarkStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamMark
        fields = ['status']


class FinalResultSerializer(serializers.ModelSerializer):
    student_roll_number = serializers.CharField(source='roll_number', read_only=True)
    student_name = serializers.SerializerMethodField()
    subject_marks = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    final_grade = serializers.SerializerMethodField()
    result_status = serializers.SerializerMethodField()
    merit_position = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_roll_number', 'student_name', 'subject_marks',
            'grand_total', 'gpa', 'final_grade', 'result_status', 'merit_position'
        ]

    def get_student_name(self, obj):
        if getattr(obj, 'full_name', None):
            return obj.full_name
        return f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip() or "N/A"

    def get_approved_marks(self, student):
        exam_type = self.context.get('exam_type')
        queryset = ExamMark.objects.filter(student=student, status='approved')
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        return queryset

    def get_subject_marks(self, student):
        marks = self.get_approved_marks(student)
        return {
            m.subject.name: {
                'writing': m.writing,
                'mcq': m.mcq,
                'practical': m.practical,
                'total': m.total,
                'grade_point': m.grade_point,
                'letter_grade': m.letter_grade,
                'is_passed': m.is_passed
            } for m in marks
        }

    def get_grand_total(self, student):
        return sum(m.total for m in self.get_approved_marks(student))

    def _calculate_gpa_details(self, student):
        marks = self.get_approved_marks(student)
        if not marks.exists():
            return {"gpa": 0.0, "grade": "F", "status": "N/A"}

        has_failed = any(not m.is_passed for m in marks)
        if has_failed:
            return {"gpa": 0.0, "grade": "F", "status": "Fail"}

        # Optional/4th subject separation logic
        compulsory_marks = []
        optional_mark = None

        for m in marks:
            if getattr(m.subject, 'is_optional', False):
                optional_mark = m
            else:
                compulsory_marks.append(m)

        if not compulsory_marks:
            return {"gpa": 0.0, "grade": "F", "status": "Fail"}

        total_gp = sum(m.grade_point for m in compulsory_marks)

        # 4th subject bonus calculation (GP - 2.00)
        if optional_mark and optional_mark.grade_point > 2.0:
            total_gp += (optional_mark.grade_point - 2.0)

        calculated_gpa = round(min(5.00, total_gp / len(compulsory_marks)), 2)

        grade_obj = GradeScale.objects.filter(grade_point__lte=calculated_gpa).order_by('-grade_point').first()
        final_grade = grade_obj.letter_grade if grade_obj else "D"

        return {"gpa": calculated_gpa, "grade": final_grade, "status": "Pass"}

    def get_gpa(self, student):
        return self._calculate_gpa_details(student)["gpa"]

    def get_final_grade(self, student):
        return self._calculate_gpa_details(student)["grade"]

    def get_result_status(self, student):
        return self._calculate_gpa_details(student)["status"]

    def get_merit_position(self, student):
        merit_dict = self.context.get('merit_map', {})
        return merit_dict.get(student.id, "N/A")