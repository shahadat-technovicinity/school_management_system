# exam/serializers.py
from rest_framework import serializers
from .models import exm_mm_exam_setup

class ExamSerializer(serializers.ModelSerializer):
    # Subject_Name মডেলের 'name' ফিল্ড থেকে রিড করবে
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = exm_mm_exam_setup
        fields = "__all__"