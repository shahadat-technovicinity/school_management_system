from rest_framework import serializers
from .models import CharacterCertificateApplication


def convert_eng_to_bng_digits(text):
    if text is None:
        return text
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


class CharacterCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterCertificateApplication
        fields = [
            'id',
            'serial_no',
            'issue_date',
            'student_name_bn',
            'father_name_bn',
            'mother_name_bn',
            'village',
            'post_office',
            'upazila',
            'district',
            'school_name_bn',
            'academic_year',
            'admission_date',
            'admission_class',
            'passing_year',
            'exam_group',
            'gpa',
            'date_of_birth',
            'status',
            'created_at',
        ]
        read_only_fields = ['status', 'issue_date']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        target_fields = [
            'serial_no', 'issue_date', 'academic_year', 'admission_date',
            'passing_year', 'gpa', 'date_of_birth'
        ]

        for field in target_fields:
            if field in ret and ret[field] is not None:
                ret[field] = convert_eng_to_bng_digits(ret[field])

        return ret


class CharacterCertificateStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterCertificateApplication
        fields = ['status']