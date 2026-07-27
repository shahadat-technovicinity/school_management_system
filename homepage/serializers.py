from rest_framework import serializers
from .models import *

# Home Page Slider Serializer
class Home_Page_SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home_Page_Slider
        fields = '__all__'


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'



# Admission Notice Serializer
class AdmissionNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionNotice
        fields = '__all__'



# Contact Message Serializer
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'



# Latter serializer
class LatterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterInfo
        fields = '__all__'





# Student & teacher staff count serializer for school dashboard

class ClassStudentCountSerializer(serializers.Serializer):
    class_name = serializers.CharField()
    total_students = serializers.IntegerField()

class SchoolDashboardStatsSerializer(serializers.Serializer):
    total_students_summary = serializers.CharField() # e.g. "৫০০০+"
    total_teachers_summary = serializers.CharField() # e.g. "২০০+"
    total_staff_summary = serializers.CharField()    # e.g. "৫০+"
    
    class_wise_students = ClassStudentCountSerializer(many=True)