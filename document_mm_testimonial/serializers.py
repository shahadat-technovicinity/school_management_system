import re
from rest_framework import serializers
from .models import StudentApplication


def convert_eng_to_bng_digits(text):
    """ইংরেজি সংখ্যাকে (0-9) বাংলা সংখ্যায় (০-৯) রূপান্তর করার ফাংশন"""
    if text is None:
        return text
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


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
            'GPA',
            'grade',
            'roll',
            'registration_no',
            'status',
            'created_at',
        ]
        read_only_fields = ['status']

    def to_representation(self, instance):
        """API রেসপন্সে পাঠানোর সময় ডেটাগুলোকে বাংলা ডিজিটে রূপান্তর করবে"""
        ret = super().to_representation(instance)
        
        target_fields = [
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
            'GPA',
            'roll',
            'registration_no',
        ]

        for field in target_fields:
            if field in ret and ret[field] is not None:
                ret[field] = convert_eng_to_bng_digits(ret[field])

        return ret


class StudentApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = ['status']