from rest_framework import serializers
from student_profile.models import StudentPersonalInfo
from .models import *

class StudentInfoFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPersonalInfo
        fields = ['roll_number', 'full_name', 'class_name', 'section']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    


 

# --- StudentMarkInputSerializer (marks_data array এর ভিতরের কাঠামো) ---
class StudentMarkInputSerializer(serializers.Serializer):
    student_roll_number = serializers.CharField(max_length=20) 
    writing = serializers.FloatField(required=False, allow_null=True)
    practical = serializers.FloatField(required=False, allow_null=True)
    mcq = serializers.FloatField(required=False, allow_null=True)

# --- MarkSubmissionSerializer (POST এর মূল লজিক) ---
class MarkSubmissionSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50) 
    exam_type = serializers.CharField(max_length=20)
    marks_data = StudentMarkInputSerializer(many=True, allow_empty=False) 

    def calculate_total(self, data):
        writing = data.get('writing') or 0
        practical = data.get('practical') or 0
        mcq = data.get('mcq') or 0
        return writing + practical + mcq

    def create(self, validated_data):
        subject = validated_data.pop('subject')
        exam_type = validated_data.pop('exam_type')
        marks_data_list = validated_data.pop('marks_data')
        
        score_objects = []
        for mark_data in marks_data_list:
            try:
                # StudentPersonalInfo মডেল থেকে roll_number ধরে ছাত্র খুঁজে বের করা
                student_obj = StudentPersonalInfo.objects.get(roll_number=mark_data['student_roll_number'])
            except StudentPersonalInfo.DoesNotExist:
                raise serializers.ValidationError({"error": f"Student with roll number {mark_data['student_roll_number']} not found."})

            total_marks = self.calculate_total(mark_data)

            mark_obj, created = ExamMark.objects.update_or_create(
                student=student_obj,
                subject=subject,
                exam_type=exam_type,
                defaults={
                    'writing': mark_data.get('writing'),
                    'practical': mark_data.get('practical'),
                    'mcq': mark_data.get('mcq'),
                    'total': total_marks,
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

# --- MarksSerializer (GET/LIST এর জন্য) ---
class MarksSerializer(serializers.ModelSerializer):
    # student_roll_number এবং full_name StudentPersonalInfo থেকে নেওয়া হচ্ছে
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    student_class_name = serializers.CharField(source='student.class_name', read_only=True)
    student_section = serializers.CharField(source='student.section', read_only=True)
    class Meta:
        model = ExamMark
        fields = [
            'id', 'student', 
            'student_name', 'student_roll_number', 
            'student_class_name', 'student_section', # ⬅️ এখন GET এ দেখা যাবে
            'subject', 'exam_type', 'writing', 'practical', 'mcq', 'total'
        ]
        read_only_fields = ['total']



class FinalResultSerializer(serializers.ModelSerializer):
    student_roll_number = serializers.CharField(source='roll_number', read_only=True)
    student_name = serializers.CharField(source='full_name', read_only=True)

    all_subjects_marks = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    pass_fail_status = serializers.SerializerMethodField()
    # Note: grade, pass/fail লজিকগুলো আপনার প্রতিষ্ঠানের নিয়ম অনুযায়ী গেট মেথডে হিসাব হবে।

    class Meta:
        model = StudentPersonalInfo
        # এই ফিল্ডগুলিই আপনার ফাইনাল রেজাল্ট টেবিলে দেখা যাবে
        fields = ('student_roll_number', 'student_name', 'all_subjects_marks', 
                  'grand_total', 'percentage', 'pass_fail_status')
    
    def get_filtered_marks(self, student):
        # View থেকে context-এর মাধ্যমে exam_type ডেটা নেওয়া হলো
        exam_type = self.context.get('exam_type')
        
        marks_records = ExamMark.objects.filter(student=student)
        if exam_type:
            # নির্দিষ্ট পরীক্ষার ধরন অনুযায়ী ফিল্টার
            marks_records = marks_records.filter(exam_type=exam_type)
        return marks_records

    def get_all_subjects_marks(self, student):
        marks_records = self.get_filtered_marks(student)
        
        subject_data = {}
        for mark in marks_records:
            subject_data[mark.subject] = {
                'total_score': mark.total,
                'status': 'Pass' if mark.total is not None and mark.total >= 33 else 'Fail' 
            }
        return subject_data
    
    def get_grand_total(self, student):
        marks_records = self.get_filtered_marks(student)
        total = sum(mark.total for mark in marks_records if mark.total is not None)
        return total

    def get_percentage(self, student):
        marks_records = self.get_filtered_marks(student)
        grand_total = self.get_grand_total(student)
        
        # ধরে নিলাম প্রতি বিষয়ের মোট নম্বর 100
        max_possible_marks = len(marks_records) * 100 
        
        if max_possible_marks == 0:
            return 0
        return round((grand_total / max_possible_marks) * 100, 2)

    def get_pass_fail_status(self, student):
        marks_records = self.get_filtered_marks(student)
        
        # যদি কোনো একটি বিষয়েও ফেল করে (ধরে নিলাম পাস মার্ক 33)
        for mark in marks_records:
            if mark.total is None or mark.total < 33: 
                return "Fail"
        return "Pass"