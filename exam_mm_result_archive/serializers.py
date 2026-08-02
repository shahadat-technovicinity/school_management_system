from rest_framework import serializers
from apps.students.models import Student
from academic_create_subject.models import Subject_Name  # ⬅️ আপনার সঠিক অ্যাপ ও মডেল ইম্পোর্ট করা হলো
from .models import ExamMark


# --- 1. Student Filter Serializer ---
# --- Student Filter Serializer ---
class StudentInfoFilterSerializer(serializers.ModelSerializer):
    # Student মডেলে first_name/last_name থাকলে সেটা মেলানোর জন্য
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'student_name', 'class_name_static', 'section_static']

    def get_student_name(self, obj):
        # Student মডেলে যদি name বা full_name ফিল্ড থাকে
        if hasattr(obj, 'full_name') and obj.full_name:
            return obj.full_name
        if hasattr(obj, 'name') and obj.name:
            return obj.name
        
        # ফার্স্ট নেম আর লাস্ট নেম থাকলে জোড়া দেবে
        first_name = getattr(obj, 'first_name', '')
        last_name = getattr(obj, 'last_name', '')
        return f"{first_name} {last_name}".strip() or "N/A"

# --- 2. Student Mark Input Serializer (marks_data-র ভেতরের স্ট্রাকচার) ---
class StudentMarkInputSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()  # Integer student ID
    writing = serializers.FloatField(required=False, allow_null=True, default=0)
    practical = serializers.FloatField(required=False, allow_null=True, default=0)
    mcq = serializers.FloatField(required=False, allow_null=True, default=0)


# --- 3. Mark Submission Serializer (POST-এর জন্য Bulk / Single Insert) ---
class MarkSubmissionSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()  # Subject-এর ID
    exam_type = serializers.CharField(max_length=20)
    marks_data = StudentMarkInputSerializer(many=True, allow_empty=False)

    def calculate_total(self, data):
        writing = data.get('writing') or 0
        practical = data.get('practical') or 0
        mcq = data.get('mcq') or 0
        return writing + practical + mcq

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

            total_marks = self.calculate_total(mark_data)

            mark_obj, created = ExamMark.objects.update_or_create(
                student=student_obj,
                subject=subject_obj,
                exam_type=exam_type,
                defaults={
                    'writing': mark_data.get('writing', 0),
                    'practical': mark_data.get('practical', 0),
                    'mcq': mark_data.get('mcq', 0),
                    'total': total_marks,
                    'status': 'pending'  # নতুন এন্ট্রি বাই-ডিফল্ট pending
                }
            )
            score_objects.append(mark_obj)

        return {'message': 'Marks successfully processed.', 'count': len(score_objects)}

    def to_representation(self, instance):
        return {
            "status": "success",
            "message": instance['message'],
            "records_processed": instance['count']
        }


# --- 4. Marks Serializer (GET / Read operations) ---
class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    student_class_name = serializers.CharField(source='student.class_name', read_only=True)
    student_section = serializers.CharField(source='student.section', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamMark
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'student_class_name', 'student_section', 'subject', 'subject_name',
            'exam_type', 'writing', 'practical', 'mcq', 'total', 'status'
        ]
        read_only_fields = ['total', 'status']


# --- 5. Admin Status Update Serializer (PATCH ONLY) ---
class MarkStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamMark
        fields = ['status']


# --- 6. Final Result Serializer ---
class FinalResultSerializer(serializers.ModelSerializer):
    student_roll_number = serializers.CharField(source='roll_number', read_only=True)
    student_name = serializers.CharField(source='full_name', read_only=True)
    all_subjects_marks = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    pass_fail_status = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ('student_roll_number', 'student_name', 'all_subjects_marks',
                  'grand_total', 'percentage', 'pass_fail_status')

    def get_filtered_marks(self, student):
        exam_type = self.context.get('exam_type')
        # রেজাল্ট শিটে শুধু Admin Approved মার্কসই যোগ হবে
        marks_records = ExamMark.objects.filter(student=student, status='approved')
        if exam_type:
            marks_records = marks_records.filter(exam_type=exam_type)
        return marks_records

    def get_all_subjects_marks(self, student):
        marks_records = self.get_filtered_marks(student)
        subject_data = {}
        for mark in marks_records:
            subject_data[mark.subject.name] = {
                'total_score': mark.total,
                'status': 'Pass' if mark.total is not None and mark.total >= 33 else 'Fail'
            }
        return subject_data

    def get_grand_total(self, student):
        marks_records = self.get_filtered_marks(student)
        return sum(mark.total for mark in marks_records if mark.total is not None)

    def get_percentage(self, student):
        marks_records = self.get_filtered_marks(student)
        grand_total = self.get_grand_total(student)
        max_possible_marks = len(marks_records) * 100
        if max_possible_marks == 0:
            return 0
        return round((grand_total / max_possible_marks) * 100, 2)

    def get_pass_fail_status(self, student):
        marks_records = self.get_filtered_marks(student)
        if not marks_records.exists():
            return "N/A"
        for mark in marks_records:
            if mark.total is None or mark.total < 33:
                return "Fail"
        return "Pass"