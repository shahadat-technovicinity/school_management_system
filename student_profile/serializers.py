from rest_framework import serializers
from .models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class GuardianDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianDetails
        # fields = '__all__'
        exclude = ['student']  


class AdditionalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails
        # fields = '__all__'
        exclude = ['student']  


class StudentFullSerializer(serializers.ModelSerializer):
    guardian_info = GuardianDetailsSerializer()
    additional_info = AdditionalDetailsSerializer()

    class Meta:
        model = Student
        fields = '__all__'

    def create(self, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        student = Student.objects.create(**validated_data)
        if guardian_data:
            GuardianDetails.objects.create(student=student, **guardian_data)
        if additional_data:
            AdditionalDetails.objects.create(student=student, **additional_data)
        return student
