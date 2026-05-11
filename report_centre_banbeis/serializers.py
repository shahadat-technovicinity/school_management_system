from rest_framework import serializers


class EnrollmentDataSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    male_students = serializers.IntegerField()
    female_students = serializers.IntegerField()
    gender_ratio = serializers.FloatField()


class TeacherInfoSerializer(serializers.Serializer):
    total_teachers = serializers.IntegerField()
    male_teachers = serializers.IntegerField()
    female_teachers = serializers.IntegerField()
    subject_experts = serializers.IntegerField()