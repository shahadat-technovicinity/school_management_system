from rest_framework import serializers
from .models import StudentApplication

class StudentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = [
            'id',
            'student_name_bn',
            'date_of_birth',
            'father_name_bn',
            'mother_name_bn',
            'village',
            'post_office',
            'upazila',
            'district',
            'passing_year',
            'academic_year',
            'exam_month',
            'board',
            'department',
            'gpa',
            'grade',
            'roll',
            'registration_no',
            'status',
            'created_at',
        ]
        read_only_fields = ['status']


class StudentApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = ['status']