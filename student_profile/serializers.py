from rest_framework import serializers
from .models import *

class StudentPersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPersonalInfo
        fields = '__all__'


class StudentGurdianInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGurdianInfo
        # fields = '__all__'
        exclude = ['student']  


class StudentAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAdditionalInfo
        # fields = '__all__'
        exclude = ['student']  


class StudentFullSerializer(serializers.ModelSerializer):
    guardian_info = StudentGurdianInfoSerializer()
    additional_info = StudentAdditionalInfoSerializer()

    class Meta:
        model = StudentPersonalInfo
        fields = '__all__'

    def create(self, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        student = StudentPersonalInfo.objects.create(**validated_data)
        if guardian_data:
            StudentGurdianInfo.objects.create(student=student, **guardian_data)
        if additional_data:
            StudentAdditionalInfo.objects.create(student=student, **additional_data)
        return student
