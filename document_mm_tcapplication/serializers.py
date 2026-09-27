from rest_framework import serializers
from .models import TCApplication


def convert_eng_to_bng_digits(text):
    if text is None:
        return text
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


class TCApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCApplication
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
            'leaving_date',
            'date_of_birth',
            'age_years',
            'age_months',
            'age_days',
            'current_class',
            'promoted_from_class',
            'promoted_to_class',
            'is_promoted',
            'fees_paid_up_to_year',
            'registration_no',
            'leaving_reason',
            'status',
            'created_at',
        ]
        read_only_fields = ['status', 'issue_date']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        target_fields = [
            'serial_no', 'issue_date', 'leaving_date', 'date_of_birth',
            'age_years', 'age_months', 'age_days', 'current_class',
            'promoted_from_class', 'promoted_to_class', 'fees_paid_up_to_year',
            'registration_no'
        ]

        for field in target_fields:
            if field in ret and ret[field] is not None:
                ret[field] = convert_eng_to_bng_digits(ret[field])

        return ret


class TCApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCApplication
        fields = ['status']