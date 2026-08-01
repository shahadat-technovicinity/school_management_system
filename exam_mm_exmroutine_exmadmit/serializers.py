# admissions/serializers.py

from rest_framework import serializers
from .models import ExamRoutine, ExamAdmit

class ExamRoutineAdmit(serializers.ModelSerializer):
    # Subject_Name মডেলের 'name' ফিল্ড থেকে নাম রিড করবে
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = ExamRoutine
        fields = '__all__'


class ExamAdmitSerializer(serializers.ModelSerializer):
    # Subject_Name মডেলের 'name' ফিল্ড থেকে নাম রিড করবে
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = ExamAdmit
        fields = '__all__'


##### admit card summary dashboard serializer

class AdmitSummarySerializer(serializers.Serializer):
    generated = serializers.IntegerField()
    pending = serializers.IntegerField()
    total = serializers.IntegerField()