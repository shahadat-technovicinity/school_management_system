# exam / serializers.py
from rest_framework import serializers
from .models import *


class stipend_stu_serializer(serializers.ModelSerializer):
    class Meta:
        model = stipend_student
        fields = "__all__"





class stipend_free_hf_serializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    fee_head_names = serializers.SerializerMethodField()

    class Meta:
        model = stipend_free_hf
        fields = [
            'id', 'student', 'student_name', 'admission_number',
            'fee_heads', 'fee_head_names',
            'concession_type', 'category', 'percent',
            'valid_from', 'valid_till', 'reason_for_concession', 'status',
        ]
        extra_kwargs = {'fee_heads': {'allow_empty': False}}

    def get_student_name(self, obj):
        return getattr(obj.student, 'full_name', str(obj.student))

    def get_fee_head_names(self, obj):
        return [h.name for h in obj.fee_heads.all()]

    def validate(self, attrs):
        inst = self.instance
        if inst and 'student' in attrs and attrs['student'] != inst.student:
            raise serializers.ValidationError({'student': "ছাত্র বদলানো যাবে না। নতুন রেকর্ড বানান।"})

        start = attrs.get('valid_from', inst.valid_from if inst else None)
        end = attrs.get('valid_till', inst.valid_till if inst else None)
        if start and end and end < start:
            raise serializers.ValidationError({'valid_till': "শেষ তারিখ শুরুর আগে হতে পারে না।"})

        heads = attrs.get('fee_heads')
        if heads is not None:
            bad = [h.name for h in heads if h.children.exists()]
            if bad:
                raise serializers.ValidationError(
                    {'fee_heads': f"শুধু শেষ স্তরের fee বাছা যাবে। এগুলোর নিচে sub category আছে: {', '.join(bad)}"}
                )
        return attrs