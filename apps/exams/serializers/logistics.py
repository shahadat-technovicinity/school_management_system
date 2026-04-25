from rest_framework import serializers
from ..models.logistics import ExamAdmitCard, ExamSeatPlan, TeacherDuty

class ExamAdmitCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAdmitCard
        fields = '__all__'

class ExamSeatPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSeatPlan
        fields = '__all__'

class TeacherDutySerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.user.get_full_name')
    
    class Meta:
        model = TeacherDuty
        fields = '__all__'
