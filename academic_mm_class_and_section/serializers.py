from rest_framework import serializers
from .models import AcademicClass, Section

class AcademicClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicClass
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'