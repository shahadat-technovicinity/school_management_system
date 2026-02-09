from rest_framework import serializers
from apps.academics.models import Class
from apps.academics.serializers.academic_years import AcademicYearSerializer    

class ClassSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer()

    class Meta:
        model = Class
        fields = ['id', 'name', 'level', 'academic_year']

    def create(self, validated_data):
        academic_year_data = validated_data.pop('academic_year')
        academic_year = AcademicYearSerializer.create(AcademicYearSerializer(), validated_data=academic_year_data)
        class_instance = Class.objects.create(academic_year=academic_year, **validated_data)
        return class_instance

    def update(self, instance, validated_data):
        academic_year_data = validated_data.pop('academic_year')
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)
        instance.academic_year = AcademicYearSerializer.update(instance.academic_year, academic_year_data)
        instance.save()
        return instance